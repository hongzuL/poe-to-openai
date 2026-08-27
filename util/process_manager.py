import asyncio
import os
import platform
import socket
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

RUN_DIR = Path("run")
LOG_DIR = Path("log")
PID_FILE = RUN_DIR / "app.pid"
LOG_FILE = LOG_DIR / "app.log"


def is_port_in_use(port: int, host: str = "127.0.0.1") -> bool:
    """跨平台使用标准库 socket 探测端口是否被占用。"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(0.5)
            return s.connect_ex((host, port)) == 0
    except Exception:
        return False


def get_pid() -> Optional[int]:
    """获取当前记录的服务 PID。"""
    if not PID_FILE.exists():
        return None
    try:
        content = PID_FILE.read_text(encoding="utf-8").strip()
        if content:
            pid = int(content)
            return pid
    except Exception:
        pass
    return None


def is_process_running(pid: Optional[int]) -> bool:
    """跨平台检查指定 PID 进程是否存活。"""
    if pid is None or pid <= 0:
        return False
    if platform.system() == "Windows":
        try:
            # 在 Windows 上使用 tasklist 检查进程
            output = subprocess.check_output(
                ["tasklist", "/FI", f"PID eq {pid}", "/FO", "CSV", "/NH"],
                text=True,
                stderr=subprocess.DEVNULL,
                creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, "CREATE_NO_WINDOW") else 0,
            )
            return str(pid) in output
        except Exception:
            return False
    else:
        try:
            os.kill(pid, 0)
            return True
        except (OSError, ProcessLookupError):
            return False


def get_server_status(expected_port: int = 39527) -> Dict[str, Any]:
    """获取服务的运行状态。"""
    pid = get_pid()
    running = is_process_running(pid)
    port_used = is_port_in_use(expected_port)

    # 如果 pid 不存在/不存活，但 pid 文件还在，清理残留 pid 文件
    if not running and PID_FILE.exists():
        try:
            PID_FILE.unlink()
        except Exception:
            pass

    return {
        "running": running,
        "pid": pid if running else None,
        "port_in_use": port_used,
        "expected_port": expected_port,
        "os": platform.system(),
        "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
    }


def start_server_process() -> Dict[str, Any]:
    """跨平台启动后端服务进程。"""
    from util.env_manager import read_env_raw

    RUN_DIR.mkdir(parents=True, exist_ok=True)
    LOG_DIR.mkdir(parents=True, exist_ok=True)

    config = read_env_raw()
    port = int(config.get("PORT", 39527))
    host = config.get("HOST", "0.0.0.0")

    pid = get_pid()
    if is_process_running(pid):
        return {"success": False, "message": f"服务已在运行 (PID {pid})"}

    if is_port_in_use(port):
        return {"success": False, "message": f"端口 {port} 已被占用，请先停止冲突进程"}

    python_bin = sys.executable
    run_script = Path(__file__).resolve().parent.parent / "run.py"

    log_fp = open(LOG_FILE, "a", encoding="utf-8")

    creationflags = 0
    start_new_session = True
    if platform.system() == "Windows":
        # Windows: 创建独立进程组与分离进程
        if hasattr(subprocess, "CREATE_NEW_PROCESS_GROUP"):
            creationflags |= subprocess.CREATE_NEW_PROCESS_GROUP
        if hasattr(subprocess, "DETACHED_PROCESS"):
            creationflags |= subprocess.DETACHED_PROCESS
        start_new_session = False

    try:
        proc = subprocess.Popen(
            [python_bin, str(run_script)],
            stdout=log_fp,
            stderr=log_fp,
            cwd=str(run_script.parent),
            creationflags=creationflags,
            start_new_session=start_new_session,
        )
        PID_FILE.write_text(str(proc.pid), encoding="utf-8")

        # 检查启动状态（等待最多 3 秒）
        for _ in range(6):
            time.sleep(0.5)
            if not is_process_running(proc.pid):
                return {"success": False, "message": "服务启动后立即退出，请检查 log/app.log 日志"}
            if is_port_in_use(port):
                return {"success": True, "pid": proc.pid, "message": f"服务启动成功 (PID {proc.pid}, http://{host}:{port})"}

        return {"success": True, "pid": proc.pid, "message": f"服务已启动 (PID {proc.pid})"}
    except Exception as e:
        return {"success": False, "message": f"启动失败: {str(e)}"}


def stop_server_process() -> Dict[str, Any]:
    """跨平台停止后端服务进程。"""
    pid = get_pid()
    if not pid or not is_process_running(pid):
        if PID_FILE.exists():
            PID_FILE.unlink(missing_ok=True)
        return {"success": True, "message": "服务未在运行"}

    try:
        if platform.system() == "Windows":
            # Windows 强制杀掉进程树
            subprocess.run(["taskkill", "/F", "/T", "/PID", str(pid)], check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        else:
            import signal
            os.kill(pid, signal.SIGTERM)
            # 等待退出
            for _ in range(10):
                time.sleep(0.5)
                if not is_process_running(pid):
                    break
            if is_process_running(pid):
                os.kill(pid, signal.SIGKILL)

        PID_FILE.unlink(missing_ok=True)
        return {"success": True, "message": f"服务已停止 (PID {pid})"}
    except Exception as e:
        PID_FILE.unlink(missing_ok=True)
        return {"success": False, "message": f"停止服务失败: {str(e)}"}


def get_latest_logs(lines: int = 100) -> str:
    """读取最新的运行日志。"""
    if not LOG_FILE.exists():
        return "暂无日志。"
    try:
        content = LOG_FILE.read_text(encoding="utf-8", errors="replace")
        all_lines = content.splitlines()
        return "\n".join(all_lines[-lines:])
    except Exception as e:
        return f"读取日志出错: {str(e)}"