#!/bin/bash
# poe-to-openai 服务管理脚本（macOS / Linux）
# 用法: ./start.sh {start|stop|restart|status|log|foreground}
set -euo pipefail
cd "$(dirname "$0")"

VENV_DIR=".venv"
RUN_DIR="run"
LOG_DIR="log"
PID_FILE="$RUN_DIR/app.pid"
LOG_FILE="$LOG_DIR/app.log"

# ---------- 环境 ----------

load_env() {
    if [ ! -f .env ]; then
        echo "错误：未找到 .env，请先运行 ./configure.sh"
        exit 1
    fi
    set -a
    . ./.env
    set +a
}

load_env_if_present() {
    if [ -f .env ]; then
        set -a
        . ./.env
        set +a
    fi
}

current_port() {
    echo "${PORT:-39527}"
}

# ---------- 端口检测 ----------

port_in_use() {
    lsof -nP -iTCP:"$1" -sTCP:LISTEN >/dev/null 2>&1
}

port_listener_pids() {
    lsof -nP -iTCP:"$1" -sTCP:LISTEN -t 2>/dev/null || true
}

# ---------- Python 环境与依赖 ----------

ensure_python() {
    if [ -x "$VENV_DIR/bin/python" ]; then
        return
    fi
    local python_bin=""
    local candidate version major minor
    for candidate in python3.13 python3.12 python3.11 python3; do
        if command -v "$candidate" >/dev/null 2>&1; then
            version=$("$candidate" -c 'import sys; print("%d.%d" % sys.version_info[:2])')
            major=${version%%.*}
            minor=${version##*.}
            if [ "$major" -ge 3 ] && [ "$minor" -ge 10 ]; then
                python_bin="$candidate"
                break
            fi
        fi
    done
    if [ -z "$python_bin" ]; then
        echo "错误：需要 Python >= 3.10，请先安装：brew install python@3.11"
        exit 1
    fi
    echo "使用 $python_bin 创建虚拟环境..."
    "$python_bin" -m venv "$VENV_DIR"
    "$VENV_DIR/bin/pip" install --quiet --upgrade pip
}

install_deps() {
    # requirements.txt 有更新时重新安装
    if [ ! -f "$VENV_DIR/.deps_installed" ] || [ requirements.txt -nt "$VENV_DIR/.deps_installed" ]; then
        echo "安装/更新依赖..."
        "$VENV_DIR/bin/pip" install --quiet -r requirements.txt
        touch "$VENV_DIR/.deps_installed"
    fi
}

# ---------- 进程状态 ----------

is_running() {
    [ -f "$PID_FILE" ] && kill -0 "$(cat "$PID_FILE")" 2>/dev/null
}

wait_pid_exit() {
    local pid=$1
    local retries=${2:-10}
    local i
    for i in $(seq 1 "$retries"); do
        if ! kill -0 "$pid" 2>/dev/null; then
            return 0
        fi
        sleep 1
    done
    if kill -0 "$pid" 2>/dev/null; then
        kill -9 "$pid" 2>/dev/null || true
    fi
}

gunicorn_cmd() {
    local host=${HOST:-0.0.0.0}
    local port=${PORT:-39527}
    local workers=${CORE_NUM:-2}
    echo "$VENV_DIR/bin/gunicorn -w $workers -t 600 -k uvicorn.workers.UvicornWorker -b $host:$port main:app"
}

# ---------- 命令 ----------

do_start() {
    load_env
    local host=${HOST:-0.0.0.0}
    local port
    port=$(current_port)

    if is_running; then
        echo "服务已在运行 (PID $(cat "$PID_FILE"))"
        exit 0
    fi
    rm -f "$PID_FILE"  # 清理陈旧 pid 文件

    # 前置检查：端口被占用（例如之前残留的实例）时直接报错，不再误报成功
    if port_in_use "$port"; then
        echo "错误：端口 $port 已被占用，可能是之前残留的进程："
        lsof -nP -iTCP:"$port" -sTCP:LISTEN
        echo
        echo "请先运行 ./start.sh stop 清理，或手动 kill 上面的进程"
        exit 1
    fi

    ensure_python
    install_deps
    mkdir -p "$RUN_DIR" "$LOG_DIR"
    echo "启动 poe-to-openai: http://$host:$port (日志: ${LOG_FILE})"
    nohup $(gunicorn_cmd) >> "$LOG_FILE" 2>&1 &
    echo $! > "$PID_FILE"

    # gunicorn 绑定失败时会重试数秒才退出，轮询最多 10 秒确认真正监听成功
    local pid
    pid=$(cat "$PID_FILE")
    local i
    for i in $(seq 1 10); do
        sleep 1
        if ! kill -0 "$pid" 2>/dev/null; then
            echo "启动失败，进程已退出。最近的日志："
            tail -5 "$LOG_FILE" 2>/dev/null || true
            rm -f "$PID_FILE"
            exit 1
        fi
        if port_listener_pids "$port" | grep -qx "$pid"; then
            echo "启动成功 (PID ${pid}, 监听 $host:$port)"
            exit 0
        fi
    done
    echo "警告：进程存活但 10 秒内未检测到端口监听，请查看 ${LOG_FILE}"
    exit 1
}

do_stop() {
    load_env_if_present
    local port
    port=$(current_port)
    local stopped=0

    if [ -f "$PID_FILE" ]; then
        local pid
        pid=$(cat "$PID_FILE")
        if kill -0 "$pid" 2>/dev/null; then
            echo "停止服务 (PID $pid)..."
            kill "$pid" 2>/dev/null || true
            wait_pid_exit "$pid" 10
            stopped=1
        fi
        rm -f "$PID_FILE"
    fi

    # 兜底：pid 文件丢失/失效但端口仍被占用时，按命令行特征清理残留实例
    if port_in_use "$port"; then
        echo "端口 $port 仍被占用，清理残留的 gunicorn 进程..."
        pkill -f "gunicorn.*main:app" 2>/dev/null || true
        sleep 2
        stopped=1
    fi

    if port_in_use "$port"; then
        echo "警告：端口 $port 仍被占用，请手动检查：lsof -nP -iTCP:$port -sTCP:LISTEN"
        exit 1
    fi

    if [ "$stopped" = "1" ]; then
        echo "已停止"
    else
        echo "服务未在运行"
    fi
}

do_status() {
    load_env_if_present
    local port
    port=$(current_port)

    if is_running; then
        echo "运行中 (PID $(cat "$PID_FILE")，端口 $port)"
    elif port_in_use "$port"; then
        echo "异常：端口 $port 被占用，但不是本脚本管理的进程（可能是残留实例）："
        lsof -nP -iTCP:"$port" -sTCP:LISTEN
        echo "可运行 ./start.sh stop 清理"
        exit 1
    else
        echo "未运行"
        exit 1
    fi
}

do_foreground() {
    load_env
    local port
    port=$(current_port)
    if port_in_use "$port"; then
        echo "错误：端口 $port 已被占用，请先 ./start.sh stop"
        exit 1
    fi
    ensure_python
    install_deps
    mkdir -p "$RUN_DIR" "$LOG_DIR"
    echo "前台运行（Ctrl+C 停止）..."
    exec $(gunicorn_cmd)
}

case "${1:-}" in
    start)      do_start ;;
    stop)       do_stop ;;
    restart)    do_stop; do_start ;;
    status)     do_status ;;
    log|logs)   tail -f "$LOG_FILE" ;;
    foreground) do_foreground ;;
    *)
        echo "用法: $0 {start|stop|restart|status|log|foreground}"
        exit 1
        ;;
esac
