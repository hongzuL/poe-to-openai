# Poe 转 OpenAI 兼容接口服务

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-green.svg)](https://fastapi.tiangolo.com/)
[![License: Apache-2.0](https://img.shields.io/badge/License-Apache%202.0-yellow.svg)](LICENSE)

基于 [Poe](https://poe.com) 官方 API 构建的 OpenAI 格式代理服务，支持 `/v1/chat/completions`、`/v1/models` 以及 `/v1/images/generations`。

**核心亮点**：支持完整的 Agent 工具调用（Tool Use / Function Calling）、Prompt 仿真降级模式、流式超时防卡死机制、强制接口鉴权与轻量化运维管理。

[English Documentation (README.md)](README.md) | [模型列表与定价 (MODELS.md)](MODELS.md) | [部署说明 (部署说明.md)](部署说明.md) | [改造总结 (改动总结.md)](改动总结.md)

---

## ✨ 核心特性

- **完整的工具调用（Tool / Function Calling）支持**：
  - **原生协议模式 (`native`)**：通过 `fastapi_poe` 底层 `stream_request_base` 协议透传 `tools`，规范传递顶层 `tool_calls` 与 `role: tool` 结果，支持完整的多轮 Agent 回路。
  - **Prompt 仿真模式 (`emulate`)**：将工具 Schema 自动注入 System Prompt，解析模型输出的 JSON 为标准 OpenAI `tool_calls`。**让原本在 Poe 上不支持 tools 的模型（如 `gemini-3.7-flash`）也能用于 Agent 客户端**。
  - **自动降级模式 (`auto`, 默认)**：优先尝试原生协议，若 Poe 上游提示不支持 tools，则自动无缝降级为仿真模式（进程内缓存判断结果）。
- **完善的超时防护与错误响应**：
  - **首事件与总耗时双重超时保护**：`POE_FIRST_EVENT_TIMEOUT`（默认 30 秒）和 `POE_STREAM_TIMEOUT`（默认 120 秒），杜绝上游无响应导致的无休止挂起。
  - **SSE 保活心跳**：仿真模式或慢响应时每 15 秒发送 `: keepalive`，防止客户端连接超时断开。
  - **精准错误透传**：遇到上游 `BotError` 或网络异常时即时返回明确错误提示。
- **企业级安全与可靠性**：
  - **强制 Bearer Token 鉴权**：通过 `CUSTOM_TOKEN` 与常量时间校验（`secrets.compare_digest`）保护所有 `/v1/` 接口，未授权直接 401。
  - **安全脱敏日志**：默认 WARNING 级别，不记录 Token 与对话明文；支持按需开启排障诊断日志（`POE_DEBUG_LOG=1`）。
  - **连接池生命周期管理**：采用 FastAPI lifespan 单例共享 `httpx.AsyncClient`，杜绝连接泄漏。
- **现代化模型映射**：
  - 收录 28 个经 Poe 官方实测的现役模型 ID（小写标准名称：`gpt-5.4`、`claude-sonnet-4.6`、`claude-opus-4.8`、`gemini-3.5-flash` 等）。
  - 支持最新生图模型（`gpt-image-2`、`flux-2-dev`、`flux-2-pro`、`nano-banana-2` 等）。
- **极简部署与运维**：
  - 提供完善的 macOS / Linux 管理脚本（`configure.sh`、`start.sh`），内置端口占用检测、依赖增量安装与安全权限管理（`.env` 权限 600）。

---

## 🚀 快速开始

### 环境要求
- macOS 或 Linux（**Python >= 3.10**）
- Poe 订阅账号，从 [https://poe.com/api_key](https://poe.com/api_key) 获取 API key

### 1. 安装与配置

```bash
# 克隆仓库
git clone https://github.com/hongzuL/poe-to-openai.git
cd poe-to-openai

# 赋予脚本执行权限
chmod +x configure.sh start.sh run.sh

# 执行交互式配置（自动生成高强度令牌，设置 .env 权限为 600）
./configure.sh
```

### 2. 服务管理

```bash
./start.sh start       # 后台启动（日志写入 log/app.log）
./start.sh status      # 查看运行状态与 PID
./start.sh log         # 实时追踪日志
./start.sh restart     # 重启服务
./start.sh stop        # 停止服务
./start.sh foreground  # 前台运行（调试用，Ctrl+C 停止）
```

---

## ⚙️ 环境变量说明 (`.env`)

| 变量名 | 说明 | 默认值 |
|---|---|---|
| `SYSTEM_TOKEN` | Poe 官方 API key（服务端持有，绝不向客户端暴露） | **必填** |
| `CUSTOM_TOKEN` | 客户端访问接口时携带的 Bearer 令牌 | **必填** |
| `HOST` / `PORT` | 监听地址与端口 | `0.0.0.0` / `39527` |
| `MODEL_MAPPING` | 单行 JSON 格式的模型映射（OpenAI 模型名 → Poe Bot 名） | 预置验证列表 |
| `POE_TOOL_MODE` | 工具调用模式：`auto`（自动降级） / `native`（仅原生） / `emulate`（仅仿真） | `auto` |
| `POE_EMULATE_BOTS` | 预设直接走仿真模式的 bot 列表（跳过原生探测） | `gemini-3.7-flash,gemini-3.6-flash` |
| `POE_STREAM_TIMEOUT` | 单个流式请求最大超时时间（秒） | `120` |
| `POE_FIRST_EVENT_TIMEOUT` | 等待首个事件的最大超时时间（秒） | `30` |
| `POE_KEEPALIVE_SECONDS` | SSE 保活心跳包间隔（秒） | `15` |
| `POE_SIMPLIFY_SCHEMAS` | 客户端发送极复杂 Schema 被 Poe 拒绝时设为 `true` | `false` |
| `POE_DEBUG_LOG` | 设为 `1` 开启 `DIAG` 诊断日志，用于排障 | `0` |
| `PROXY_TYPE` 等 | 服务端连接 `api.poe.com` 的出站代理（`http` 或 `socks5`） | 留空直连 |

---

## 📡 接口调用示例

- **Base URL**: `http://<服务器IP>:39527`
- **Headers**: `Authorization: Bearer <CUSTOM_TOKEN>`

### 1. 模型列表
```bash
curl http://127.0.0.1:39527/v1/models \
  -H "Authorization: Bearer <CUSTOM_TOKEN>"
```

### 2. 聊天对话（支持 Function Calling）
```bash
curl http://127.0.0.1:39527/v1/chat/completions \
  -H "Authorization: Bearer <CUSTOM_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-4o",
    "messages": [{"role": "user", "content": "北京现在的天气怎么样？"}],
    "tools": [{
      "type": "function",
      "function": {
        "name": "get_current_weather",
        "description": "获取指定城市的天气",
        "parameters": {
          "type": "object",
          "properties": {
            "location": {"type": "string", "description": "城市名，例如：北京"}
          },
          "required": ["location"]
        }
      }
    }]
  }'
```

### 3. 图像生成
```bash
curl http://127.0.0.1:39527/v1/images/generations \
  -H "Authorization: Bearer <CUSTOM_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "dall-e-3",
    "prompt": "赛博朋克风格的雨夜城市，霓虹灯倒影",
    "size": "1024x1024"
  }'
```

---

## 🧪 端到端测试

项目内置了自动化测试套件：

```bash
CUSTOM_TOKEN=<你的CUSTOM_TOKEN> python3 test_tool_use.py
```

测试覆盖：
- 401 鉴权拦截验证
- 非流式工具调用
- 完整多轮 Agent 结果回传回路
- 流式 SSE 工具调用

---

## 📄 开源许可

本项目遵循 [Apache-2.0 License](LICENSE)。
