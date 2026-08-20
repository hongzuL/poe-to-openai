#!/bin/bash
# poe-to-openai 交互式配置脚本（macOS / Linux）
# 生成 .env 文件（权限 600），包含 Poe API key 和强随机访问令牌
set -euo pipefail
cd "$(dirname "$0")"

echo "=== poe-to-openai 配置向导 ==="
echo

# 1. Poe API key
read -r -s -p "请输入 Poe API key（从 https://poe.com/api_key 获取，输入不回显）: " POE_KEY
echo
# 去掉粘贴可能带入的空白字符
POE_KEY=$(printf '%s' "$POE_KEY" | tr -d '[:space:]')
if [ -z "$POE_KEY" ]; then
    echo "错误：Poe API key 不能为空"
    exit 1
fi
# 检测重复粘贴（无回显输入时容易多粘一次）：内容恰好重复两遍则自动取单份
key_len=${#POE_KEY}
if [ "$key_len" -gt 80 ]; then
    half=$((key_len / 2))
    if [ $((half * 2)) -eq "$key_len" ] && [ "${POE_KEY:0:$half}" = "${POE_KEY:$half}" ]; then
        echo "提示：检测到 key 被重复粘贴了两次，已自动取单份"
        POE_KEY="${POE_KEY:0:$half}"
    else
        echo "错误：key 长度 $key_len 异常（Poe API key 通常为 50 字符左右），请检查后重跑本脚本"
        exit 1
    fi
fi

# 2. 生成强随机 CUSTOM_TOKEN
CUSTOM_TOKEN="sk-$(openssl rand -hex 24)"
echo
echo "已生成强随机访问令牌（CUSTOM_TOKEN）："
echo "    $CUSTOM_TOKEN"
echo "客户端调用本服务时用它作为 API key，请妥善保存。"
echo

# 3. 监听地址与端口
read -r -p "监听地址 [0.0.0.0]（仅本机访问请填 127.0.0.1）: " HOST
HOST=${HOST:-0.0.0.0}
read -r -p "监听端口 [39527]: " PORT
PORT=${PORT:-39527}

# 4. 模型映射
DEFAULT_MAPPING='{"gpt-5.4":"gpt-5.4","gpt-4o":"gpt-4o","gpt-4o-mini":"gpt-4o-mini","claude-sonnet-4.6":"claude-sonnet-4.6","claude-opus-4.8":"claude-opus-4.8","gemini-3.5-flash":"gemini-3.5-flash","gemini-3.1-pro":"gemini-3.1-pro","grok-4.6":"grok-4.6","dall-e-3":"gpt-image-2","nano-banana-2":"nano-banana-2"}'
echo
echo "默认模型映射：$DEFAULT_MAPPING"
read -r -p "使用默认映射？[Y/n] " USE_DEFAULT
USE_DEFAULT=${USE_DEFAULT:-Y}
if [ "$USE_DEFAULT" = "n" ] || [ "$USE_DEFAULT" = "N" ]; then
    read -r -p "请输入单行 JSON 映射（OpenAI 模型名 -> Poe bot 名）: " MODEL_MAPPING
    if [ -z "$MODEL_MAPPING" ]; then
        echo "未输入，使用默认映射"
        MODEL_MAPPING="$DEFAULT_MAPPING"
    fi
else
    MODEL_MAPPING="$DEFAULT_MAPPING"
fi

# 5. 写入 .env（权限 600，仅所有者可读写）
umask 077
cat > .env <<EOF
SYSTEM_TOKEN=$POE_KEY
CUSTOM_TOKEN=$CUSTOM_TOKEN
HOST=$HOST
PORT=$PORT
MODEL_MAPPING='$MODEL_MAPPING'
ALLOWED_ORIGINS=
PROXY_TYPE=
PROXY_HOST=
PROXY_PORT=
PROXY_USERNAME=
PROXY_PASSWORD=
POE_SIMPLIFY_SCHEMAS=false
EOF
chmod 600 .env

echo
echo "配置完成，已写入 .env（权限 600）。"
echo "如需调整模型映射、代理等，直接编辑 .env 即可（各字段含义见 .env.example）。"
echo "下一步：./start.sh start"
