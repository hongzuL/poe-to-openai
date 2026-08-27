#!/usr/bin/env python3
"""poe-to-openai 统一跨平台管理脚本 (Windows / macOS / Linux)

用法:
  python manager.py              # 启动服务并在浏览器中打开 Web UI 控制台
  python manager.py ui           # 打开 Web UI 控制台
  python manager.py start        # 启动后台服务
  python manager.py stop         # 停止后台服务
  python manager.py restart      # 重启服务
  python manager.py status       # 检查运行状态
  python manager.py log          # 实时查看日志
  python manager.py run          # 前台运行服务 (开发调试)
"""
import argparse
import os
import platform
import sys
import time
import webbrowser
from pathlib import Path

# 添加当前目录到 sys.path
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

from util.env_manager import ENV_PATH, generate_custom_token, read_env_raw, save_env_config
from util.process_manager import (
    LOG_FILE,
    get_latest_logs,
    get_pid,
    get_server_status,
    is_port_in_use,
    is_process_running,
    start_server_process,
    stop_server_process,
)


def ensure_env():
    """若不存在 .env 文件，引导或初始化默认配置。"""
    if not ENV_PATH.exists():
        print("未检测到 .env 配置文件，正在初始化默认配置...")
        token = generate_custom_token()
        save_env_config({"CUSTOM_TOKEN": token})
        print(f"已生成初始访问令牌: {token}")


def cmd_start():
    ensure_env()
    cfg = read_env_raw()
    port = int(cfg.get("PORT", 39527))
    host = cfg.get("HOST", "0.0.0.0")

    print(f"[{platform.system()}] 正在启动 poe-to-openai...")
    res = start_server_process()
    if res.get("success"):
        print(f"启动成功! PID: {res.get('pid')}")
        print(f"服务地址: http://127.0.0.1:{port}")
        print(f"控制台:   http://127.0.0.1:{port}/ui")
    else:
        print(f"启动失败: {res.get('message')}")
        sys.exit(1)


def cmd_stop():
    print(f"[{platform.system()}] 正在停止 poe-to-openai...")
    res = stop_server_process()
    print(res.get("message", "已停止"))


def cmd_restart():
    cmd_stop()
    time.sleep(1)
    cmd_start()


def cmd_status():
    cfg = read_env_raw()
    port = int(cfg.get("PORT", 39527))
    st = get_server_status(expected_port=port)
    print("=" * 40)
    print("poe-to-openai 服务状态")
    print("=" * 40)
    print(f"操作系统:   {st['os']}")
    print(f"Python版本: {st['python_version']}")
    print(f"监听端口:   {port} ({'端口占用中' if st['port_in_use'] else '端口空闲'})")
    if st["running"]:
        print(f"运行状态:   运行中 (PID: {st['pid']})")
        print(f"Web 控制台: http://127.0.0.1:{port}/ui")
    else:
        print("运行状态:   未运行")
    print("=" * 40)


def cmd_log():
    if not LOG_FILE.exists():
        print("暂无日志文件")
        return
    print(f"--- 最近日志 ({LOG_FILE}) ---")
    print(get_latest_logs(lines=50))
    print("\n[提示] 按 Ctrl+C 退出日志跟踪...")
    try:
        with open(LOG_FILE, "r", encoding="utf-8", errors="replace") as f:
            f.seek(0, os.SEEK_END)
            while True:
                line = f.readline()
                if line:
                    print(line, end="", flush=True)
                else:
                    time.sleep(0.5)
    except KeyboardInterrupt:
        print("\n已退出日志查看")


def cmd_run():
    """前台运行服务 (方便调试和直接查看控制台输出)"""
    ensure_env()
    cfg = read_env_raw()
    port = int(cfg.get("PORT", 39527))
    host = cfg.get("HOST", "0.0.0.0")

    if is_port_in_use(port):
        print(f"错误: 端口 {port} 已被占用，请先停止冲突进程")
        sys.exit(1)

    import uvicorn
    from main import app

    print(f"[{platform.system()}] 前台启动 poe-to-openai: http://{host}:{port}")
    print(f"控制台地址: http://127.0.0.1:{port}/ui (Ctrl+C 停止)")
    uvicorn.run(app, host=host, port=port)


def cmd_ui():
    """启动服务并自动打开浏览器控制台"""
    ensure_env()
    cfg = read_env_raw()
    port = int(cfg.get("PORT", 39527))
    ui_url = f"http://127.0.0.1:{port}/ui"

    st = get_server_status(expected_port=port)
    if not st["running"]:
        print(f"服务未在运行，正在后台启动...")
        res = start_server_process()
        if not res.get("success"):
            print(f"启动失败: {res.get('message')}")
            sys.exit(1)
        time.sleep(1)

    print(f"正在打开 Web UI 控制台: {ui_url}")
    try:
        webbrowser.open(ui_url)
    except Exception as e:
        print(f"打开浏览器失败: {e}")
    print("控制台已就绪。")


def cmd_config():
    """交互式配置向导 (跨平台支持 Windows / macOS / Linux)。"""
    import getpass
    import json
    import re
    from util.env_manager import DEFAULT_MODEL_MAPPING

    print("=" * 50)
    print(" poe-to-openai 交互式配置向导")
    print("=" * 50)
    print()

    current = read_env_raw()

    # 1. Poe API key
    current_key_preview = (" (当前已配置: " + current["SYSTEM_TOKEN"][:4] + "****" + current["SYSTEM_TOKEN"][-4:] + ")") if current.get("SYSTEM_TOKEN") else ""
    print(f"1. 请输入 Poe API key{current_key_preview}")
    print("   获取地址: https://poe.com/api_key (输入时可能不回显，直接粘贴后回车)")
    poe_key = getpass.getpass("   Poe API key: ").strip()
    if not poe_key and not current.get("SYSTEM_TOKEN"):
        poe_key = input("   未读取到输入，请明文输入: ").strip()

    updates = {}
    if poe_key:
        poe_key = re.sub(r"\s+", "", poe_key)
        # 检测重复粘贴
        if len(poe_key) > 80:
            half = len(poe_key) // 2
            if poe_key[:half] == poe_key[half:]:
                print("   [提示] 检测到 key 被重复粘贴了两次，已自动去重。")
                poe_key = poe_key[:half]
        updates["SYSTEM_TOKEN"] = poe_key

    # 2. 生成或保留 CUSTOM_TOKEN
    old_custom = current.get("CUSTOM_TOKEN", "")
    if old_custom:
        print(f"\n2. 当前访问令牌 (CUSTOM_TOKEN): {old_custom}")
        regen = input("   是否重新生成随机令牌？[y/N]: ").strip().lower()
        if regen in ("y", "yes"):
            new_token = generate_custom_token()
            updates["CUSTOM_TOKEN"] = new_token
            print(f"   已生成新令牌: {new_token}")
        else:
            updates["CUSTOM_TOKEN"] = old_custom
    else:
        new_token = generate_custom_token()
        updates["CUSTOM_TOKEN"] = new_token
        print(f"\n2. 已为您生成强随机访问令牌 (CUSTOM_TOKEN):\n   {new_token}")

    # 3. 监听地址与端口
    host_default = current.get("HOST", "0.0.0.0")
    print(f"\n3. 监听地址 [{host_default}] (仅本机访问可填 127.0.0.1): ", end="")
    host_input = input().strip()
    updates["HOST"] = host_input if host_input else host_default

    port_default = current.get("PORT", "39527")
    print(f"   监听端口 [{port_default}]: ", end="")
    port_input = input().strip()
    updates["PORT"] = int(port_input) if port_input else int(port_default)

    # 4. 模型映射
    print(f"\n4. 模型映射设置")
    use_default = input("   使用默认验证模型映射 (GPT-4o, Claude 3.5, Gemini 2.0 等)？[Y/n]: ").strip().lower()
    if use_default in ("n", "no"):
        print("   请输入单行 JSON 模型映射: ", end="")
        custom_mapping = input().strip()
        if custom_mapping:
            updates["MODEL_MAPPING"] = custom_mapping
    else:
        updates["MODEL_MAPPING"] = current.get("MODEL_MAPPING", json.dumps(DEFAULT_MODEL_MAPPING, ensure_ascii=False))

    save_env_config(updates)
    print("\n" + "=" * 50)
    print(" 配置已成功保存至 .env 文件！")
    print("=" * 50)
    print("\n您现在可以启动服务：")
    if platform.system() == "Windows":
        print("  - 双击 start.bat 或运行 python manager.py")
    else:
        print("  - 运行 ./start.sh ui 或 python manager.py")


def main():
    parser = argparse.ArgumentParser(description="poe-to-openai 多系统统一管理工具")
    parser.add_argument(
        "action",
        nargs="?",
        default="ui",
        choices=["ui", "start", "stop", "restart", "status", "log", "logs", "run", "config", "configure"],
        help="执行的操作 (默认: ui 打开控制台)",
    )
    args = parser.parse_args()

    action = args.action.lower()
    if action in ("config", "configure"):
        cmd_config()
    elif action == "ui":
        cmd_ui()
    elif action == "start":
        cmd_start()
    elif action == "stop":
        cmd_stop()
    elif action == "restart":
        cmd_restart()
    elif action == "status":
        cmd_status()
    elif action in ("log", "logs"):
        cmd_log()
    elif action == "run":
        cmd_run()


if __name__ == "__main__":
    main()