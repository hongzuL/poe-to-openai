#!/bin/bash
# Docker 容器内使用的前台启动脚本
set -e

mkdir -p ./log

core_num=${CORE_NUM:-2}
time_out=${TIME_OUT:-600}
host=${HOST:-0.0.0.0}
port=${PORT:-39527}

echo "bind: $host:$port, workers: $core_num, timeout: $time_out"

exec gunicorn -w "$core_num" -t "$time_out" -k uvicorn.workers.UvicornWorker -b "$host:$port" main:app
