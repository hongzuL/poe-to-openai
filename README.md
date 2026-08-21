# Poe to OpenAI API Bridge

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-green.svg)](https://fastapi.tiangolo.com/)
[![License: Apache-2.0](https://img.shields.io/badge/License-Apache%202.0-yellow.svg)](LICENSE)

An enhanced proxy service that converts the official [Poe](https://poe.com) API to OpenAI-compatible endpoints (`/v1/chat/completions`, `/v1/models`, `/v1/images/generations`).

[中文说明 (README_ZH.md)](README_ZH.md) | [模型列表与定价 (MODELS.md)](MODELS.md) | [部署说明 (部署说明.md)](部署说明.md) | [改造总结 (改动总结.md)](改动总结.md)

---

## ✨ Key Features

- **Full Tool / Function Calling Support**:
  - **Native Protocol (`native`)**: Directly forwards tool schemas to Poe via `stream_request_base`, passing `tool_calls` and `role: tool` messages as protocol-level fields. Completes full multi-turn agent loops.
  - **Prompt Emulation (`emulate`)**: Automatically injects tool schemas into system prompts and parses model JSON outputs into standard OpenAI `tool_calls`. Enables tool use for models where Poe doesn't natively expose function calling (e.g., `gemini-3.7-flash`).
  - **Automatic Fallback (`auto`, Default)**: Tries native protocol first; if rejected with unsupported tool errors, automatically falls back to emulation mode with in-process caching.
- **Robust Timeout & Error Handling**:
  - **Streaming Timeout Protection**: `POE_STREAM_TIMEOUT` (default: 120s) and `POE_FIRST_EVENT_TIMEOUT` (default: 30s) prevent silent hangs when upstream bots fail to respond.
  - **SSE Keepalive**: Sends `: keepalive` heartbeats every 15s to keep connections alive during emulation buffering.
  - **Clear Error Propagation**: Translates upstream Poe errors (e.g. `BotError`) directly into informative messages for clients.
- **Enterprise Security & Reliability**:
  - **Mandatory Bearer Authentication**: Constant-time token verification (`secrets.compare_digest`) via `CUSTOM_TOKEN` protecting all `/v1/` routes.
  - **Sanitized Logging**: Minimal log footprint by default (WARNING level); no credential leaks. Optional diagnostic tracing (`POE_DEBUG_LOG=1`).
  - **Connection Pooling**: Uses FastAPI lifespan-managed singleton `httpx.AsyncClient` avoiding connection leaks.
- **Modernized Model Support**:
  - Validated lowercase model mappings matching current Poe bots (`gpt-5.4`, `claude-sonnet-4.6`, `claude-opus-4.8`, `gemini-3.5-flash`, etc.).
  - Up-to-date image generation models (`gpt-image-2`, `flux-2-dev`, `flux-2-pro`, `nano-banana-2`, `seedream-5.0-pro`).
- **Production-Ready Deployment**:
  - Dedicated macOS / Linux management scripts (`configure.sh`, `start.sh`) with dependency caching and port health check.

---

## 🚀 Quick Start

### Prerequisites
- macOS or Linux with **Python >= 3.10**
- A Poe subscription and API Key from [https://poe.com/api_key](https://poe.com/api_key)

### 1. Installation & Configuration

```bash
# Clone the repository
git clone https://github.com/hongzuL/poe-to-openai.git
cd poe-to-openai

# Make scripts executable
chmod +x configure.sh start.sh run.sh

# Run interactive configuration (.env with permission 600)
./configure.sh
```

### 2. Service Management

```bash
./start.sh start       # Start in background (logs to log/app.log)
./start.sh status      # Check running status & PID
./start.sh log         # Follow real-time logs
./start.sh restart     # Restart service
./start.sh stop        # Stop service
./start.sh foreground  # Run in foreground for debugging
```

---

## ⚙️ Configuration Reference (`.env`)

| Variable | Description | Default |
|---|---|---|
| `SYSTEM_TOKEN` | Official Poe API key (server-side only, never exposed) | **Required** |
| `CUSTOM_TOKEN` | Bearer token for client authentication (generated via `configure.sh`) | **Required** |
| `HOST` / `PORT` | Listening address and port | `0.0.0.0` / `39527` |
| `MODEL_MAPPING` | JSON string mapping OpenAI model IDs to Poe bot IDs | Validated JSON |
| `POE_TOOL_MODE` | `auto` (default fallback), `native` (strict), or `emulate` (prompt-based) | `auto` |
| `POE_EMULATE_BOTS` | Comma-separated bot list to directly use emulation without probing | `gemini-3.7-flash,gemini-3.6-flash` |
| `POE_STREAM_TIMEOUT` | Max stream timeout in seconds | `120` |
| `POE_FIRST_EVENT_TIMEOUT` | Max time in seconds waiting for the first stream event | `30` |
| `POE_KEEPALIVE_SECONDS` | SSE keepalive heartbeat interval | `15` |
| `POE_SIMPLIFY_SCHEMAS` | Set `true` if downstream clients send complex schemas rejected by Poe | `false` |
| `POE_DEBUG_LOG` | Set `1` to enable `DIAG` logs for request/response tracing | `0` |
| `PROXY_TYPE` etc. | Outbound proxy (`http` or `socks5`) when connecting to `api.poe.com` | Optional |

---

## 📡 API Usage Examples

Base URL: `http://<server-ip>:39527`  
Header: `Authorization: Bearer <CUSTOM_TOKEN>`

### 1. List Models
```bash
curl http://127.0.0.1:39527/v1/models \
  -H "Authorization: Bearer <CUSTOM_TOKEN>"
```

### 2. Chat Completions (with Tool Calling)
```bash
curl http://127.0.0.1:39527/v1/chat/completions \
  -H "Authorization: Bearer <CUSTOM_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-4o",
    "messages": [{"role": "user", "content": "What is the weather in Tokyo?"}],
    "tools": [{
      "type": "function",
      "function": {
        "name": "get_weather",
        "description": "Get current weather for a city",
        "parameters": {
          "type": "object",
          "properties": {
            "city": {"type": "string"}
          },
          "required": ["city"]
        }
      }
    }]
  }'
```

### 3. Image Generation
```bash
curl http://127.0.0.1:39527/v1/images/generations \
  -H "Authorization: Bearer <CUSTOM_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "dall-e-3",
    "prompt": "Cyberpunk city in heavy rain, neon lights",
    "size": "1024x1024"
  }'
```

---

## 🧪 Testing

Run the included end-to-end verification suite:

```bash
CUSTOM_TOKEN=<your_custom_token> python3 test_tool_use.py
```

Tests include:
- Unauthorized (401) check
- Non-streaming tool calls
- Multi-turn Agent loop with tool results
- Streaming SSE tool calls

---

## 📄 License

Apache-2.0 License. See [LICENSE](LICENSE) for details.
