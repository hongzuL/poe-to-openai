# Poe 可用模型与定价一览表 (Poe Models & Pricing Catalog)

> **说明**：数据来自 Poe 官方 API `/v1/models` 响应，涵盖全部 **341** 个官方及热门模型。
> - **输入/输出定价**：换算为 **$ / 1M Tokens**（每百万 Tokens 美元价格），方便与各官方 API 直观比对。
> - **图像生成定价**：标注为 **$/张 (Per Image)** 或单次点数。
> - **特性标记**：🛠️ 支持工具/函数调用 (Tools) ｜ 🌐 支持联网搜索 (Web Search) ｜ 🧠 支持思考推理 (Reasoning) ｜ 👁️ 支持多模态视觉 (Vision)。
> - **在项目中使用**：只需在 `.env` 的 `MODEL_MAPPING` 中将客户端请求的模型名称映射到对应的 **Poe Bot ID** 即可。

## 目录 (Table of Contents)

- [🧠 Anthropic (Claude 系列)](#anthropic) （共 8 个）
- [⚡ OpenAI (GPT / o 系列)](#openai) （共 39 个）
- [🌐 Google (Gemini / Gemma 系列)](#google) （共 17 个）
- [🚀 xAI (Grok 系列)](#xai) （共 14 个）
- [🔍 DeepSeek 系列](#deepseek) （共 17 个）
- [🦙 Meta (Llama 系列)](#meta) （共 5 个）
- [🇨🇳 阿里 (Qwen / 通义千问 系列)](#阿里) （共 32 个）
- [🌪️ Mistral AI 系列](#mistral) （共 9 个）
- [🎨 图像生成模型 (Image Generation)](#图像生成模型) （共 52 个）
- [🎵 音视频与专用工具模型 (Audio / Video / Embeddings)](#音视频与专用工具模型) （共 71 个）
- [📦 其他主流与社区模型 (Other / Community Models)](#其他主流与社区模型) （共 77 个）
- [如何在本项目中配置模型映射](#如何在本项目中配置模型映射)
- [自动更新模型与价格数据](#自动更新模型与价格数据)

---

## <a id='anthropic'></a>🧠 Anthropic (Claude 系列) (共 8 个)

| Poe Bot ID | 显示名称 | 上下文 | 最大输出 | 输入价格 / 1M | 输出价格 / 1M | 缓存读取 / 1M | 特性 | 描述 |
|---|---|---|---|---|---|---|---|---|
| `claude-code` | Claude-Code | - | - | - | - | - | - | A powerful assistant that can read, write, and analyze fi... |
| `claude-haiku-4.5` | Claude-Haiku-4.5 | 192k | 64k | $0.859 | $4.29 | $0.086 | 🛠️ 🌐 🧠 👁️ | Claude Haiku 4.5 is Anthropic’s fastest and most efficien... |
| `claude-opus-4.5` | Claude-Opus-4.5 | 196k | 64k | $4.29 | $21.46 | $0.429 | 🛠️ 🌐 🧠 👁️ | Claude Opus 4.5 from Anthropic, supports customizable thi... |
| `claude-opus-4.6` | Claude-Opus-4.6 | 983k | 128k | $4.29 | $21.46 | $0.429 | 🛠️ 🌐 🧠 👁️ | Claude Opus 4.6 is Anthropic’s most advanced AI model, bu... |
| `claude-opus-4.7` | Claude-Opus-4.7 | 1M | 128k | $4.29 | $21.46 | $0.429 | 🛠️ 🌐 🧠 👁️ | Anthropic’s flagship model for enterprise-grade knowledge... |
| `claude-opus-4.8` | Claude-Opus-4.8 | 1M | 128k | $4.29 | $21.46 | $0.429 | 🛠️ 🌐 🧠 👁️ | Anthropic's flagship model for enterprise-grade knowledge... |
| `claude-sonnet-4.5` | Claude-Sonnet-4.5 | 983k | 32k | $2.58 | $12.88 | $0.258 | 🛠️ 🌐 🧠 👁️ | Claude Sonnet 4.5 represents a major leap forward in AI c... |
| `claude-sonnet-4.6` | Claude-Sonnet-4.6 | 983k | 128k | $2.58 | $12.88 | $0.258 | 🛠️ 🌐 🧠 👁️ | Claude Sonnet 4.6 from Anthropic is built for high-qualit... |


## <a id='openai'></a>⚡ OpenAI (GPT / o 系列) (共 39 个)

| Poe Bot ID | 显示名称 | 上下文 | 最大输出 | 输入价格 / 1M | 输出价格 / 1M | 缓存读取 / 1M | 特性 | 描述 |
|---|---|---|---|---|---|---|---|---|
| `gpt-3.5-turbo` | GPT-3.5-Turbo | 16k | 2k | $0.455 | $1.36 | - | 🛠️ 👁️ | OpenAI’s GPT 3.5 Turbo model is a powerful language gener... |
| `gpt-3.5-turbo-instruct` | GPT-3.5-Turbo-Instruct | 3k | 1k | $1.36 | $1.82 | - | 🛠️ 👁️ | This model is a variant of GPT-3.5 Turbo tuned for instru... |
| `gpt-3.5-turbo-raw` | GPT-3.5-Turbo-Raw | 4k | 2k | $0.455 | $1.36 | - | 🛠️ 👁️ | Powered by gpt-3.5-turbo without a system prompt. |
| `gpt-4-turbo` | GPT-4-Turbo | 128k | 4k | $9.09 | $27.27 | - | 🛠️ 👁️ | Powered by OpenAI's GPT-4 Turbo. For most tasks, https://... |
| `gpt-4.1` | GPT-4.1 | 1M | 32k | $1.82 | $7.27 | $0.455 | 🛠️ 👁️ | OpenAI’s GPT-4.1 significantly improves on past models in... |
| `gpt-4.1-mini` | GPT-4.1-mini | 1M | 32k | $0.364 | $1.45 | $0.091 | 🛠️ 👁️ | GPT-4.1 mini is a small, fast & affordable model that mat... |
| `gpt-4.1-nano` | GPT-4.1-nano | 1M | 32k | $0.091 | $0.364 | $0.023 | 🛠️ 👁️ | GPT-4.1 nano is an extremely fast and cheap model, ideal ... |
| `gpt-4o` | GPT-4o | 128k | 8k | - | - | - | 🛠️ 👁️ | OpenAI's GPT-4o answers user prompts in a natural, engagi... |
| `gpt-4o-aug` | GPT-4o-Aug | 128k | 8k | $2.27 | $9.09 | $1.14 | 🛠️ 👁️ | OpenAI's most powerful model, GPT-4o, using the August 20... |
| `gpt-4o-mini` | GPT-4o-mini | 124k | 4k | $0.136 | $0.545 | $0.068 | 🛠️ 👁️ | This intelligent small model from OpenAI is significantly... |
| `gpt-4o-search` | GPT-4o-Search | 128k | 8k | $2.27 | $9.09 | - | 🛠️ | OpenAI's fine-tuned model for searching the web for real-... |
| `gpt-5` | GPT-5 | 400k | 128k | $1.14 | $9.09 | $0.114 | 🛠️ 🌐 🧠 👁️ | OpenAI’s most advanced general model with significantly i... |
| `gpt-5-mini` | GPT-5-mini | 400k | 128k | $0.227 | $1.82 | $0.023 | 🛠️ 🌐 🧠 👁️ | GPT-5 mini is a small, fast & affordable model that match... |
| `gpt-5-nano` | GPT-5-nano | 400k | 128k | $0.045 | $0.364 | $0.0045 | 🛠️ 🌐 🧠 👁️ | GPT-5 nano is an extremely fast and cheap model, ideal fo... |
| `gpt-5-pro` | GPT-5-Pro | 400k | 128k | $13.64 | $109.09 | - | 🛠️ 🌐 🧠 👁️ | OpenAI’s latest flagship model with significantly improve... |
| `gpt-5.1` | GPT-5.1 | 400k | 128k | $1.14 | $9.09 | $0.114 | 🛠️ 🌐 🧠 👁️ | OpenAI’s flagship general‑purpose model, built for advanc... |
| `gpt-5.2` | GPT-5.2 | 400k | 128k | $1.59 | $12.73 | $0.159 | 🛠️ 🌐 🧠 👁️ | GPT-5.2 is a state-of-the-art AI model from OpenAI design... |
| `gpt-5.2-pro` | GPT-5.2-Pro | 400k | 128k | $19.09 | $152.73 | - | 🛠️ 🌐 🧠 👁️ | A powerful reasoning model that is ideal for your most co... |
| `gpt-5.3-codex` | GPT-5.3-Codex | 400k | 128k | $1.59 | $12.73 | $0.159 | 🛠️ 🧠 👁️ | GPT‑5.3‑Codex excels in software development. It understa... |
| `gpt-5.4` | GPT-5.4 | 1.1M | 128k | $2.27 | $13.64 | $0.227 | 🛠️ 🌐 🧠 👁️ | GPT-5.4 is the most capable AI model from OpenAI, built f... |
| `gpt-5.4-mini` | GPT-5.4-Mini | 400k | 128k | $0.682 | $4.09 | $0.068 | 🛠️ 🌐 🧠 👁️ | GPT‑5.4 Mini is a fast, affordable general‑purpose model ... |
| `gpt-5.4-nano` | GPT-5.4-Nano | 400k | 128k | $0.182 | $1.14 | $0.018 | 🛠️ 🌐 🧠 👁️ | GPT‑5.4 Nano is the fastest and most cost‑efficient model... |
| `gpt-5.4-pro` | GPT-5.4-Pro | 1.1M | 128k | $27.27 | $163.64 | - | 🛠️ 🌐 🧠 👁️ | A smarter, more precise version of GPT-5.4 that leverages... |
| `gpt-oss-120b` | GPT-OSS-120B | - | - | $0.151 | $0.606 | - | 🛠️ | GPT-OSS-120B is OpenAI's open-weight general-purpose mode... |
| `gpt-oss-120b-cs` | GPT-OSS-120B-CS | 128k | - | $0.353 | $0.758 | - | 🛠️ | World’s fastest inference for GPT OSS 120B with Cerebras.... |
| `gpt-oss-120b-t` | GPT-OSS-120B-T | 128k | - | - | - | - | 👁️ | OpenAI's GPT-OSS-120B delivers sophisticated chain-of-tho... |
| `gpt-oss-20b-n` | GPT-OSS-20B-N | - | - | - | - | - | 👁️ | gpt-oss-20b is an open-weight 21B parameter model release... |
| `gpt-oss-20b-t` | GPT-OSS-20B-T | - | - | - | - | - | 👁️ | OpenAI's GPT-OSS-20B provides powerful chain-of-thought r... |
| `gpt-researcher` | GPT-Researcher | - | - | - | - | - | - | GPT Researcher is an agent that conducts deep research on... |
| `gptzero` | GPTZero | - | - | - | - | - | - | GPTZero is a deep-learning-driven platform designed to an... |
| `o1` | o1 | 200k | 100k | $13.64 | $54.55 | - | 🛠️ 🧠 👁️ | OpenAI's o1 is designed to reason before it responds and ... |
| `o1-pro` | o1-pro | 200k | 100k | $136.36 | $545.45 | - | 🛠️ 🌐 🧠 👁️ | OpenAI’s o1-pro highly capable reasoning model, tailored ... |
| `o3` | o3 | 200k | 100k | $1.82 | $7.27 | $0.455 | 🛠️ 🧠 👁️ | o3 provides state-of-the-art intelligence on a variety of... |
| `o3-mini` | o3-mini | 200k | 100k | $1.00 | $4.00 | - | 🛠️ 🧠 👁️ | o3-mini is OpenAI's reasoning model, providing high intel... |
| `o3-mini-high` | o3-mini-high | 200k | 100k | $1.00 | $4.00 | - | 🛠️ 🧠 👁️ | o3-mini-high is OpenAI's most recent reasoning model with... |
| `o3-pro` | o3-pro | 200k | 100k | $18.18 | $72.73 | - | 🛠️ 🧠 👁️ | o3-pro is a well-rounded and powerful model across domain... |
| `o4-mini` | o4-mini | 200k | 100k | $1.00 | $4.00 | $0.250 | 🛠️ 🧠 👁️ | o4-mini provides high intelligence on a variety of tasks ... |
| `openai-gpt-oss-120b` | OpenAI-GPT-OSS-120B | 128k | - | - | - | - | 👁️ | GPT-OSS-120b is a high-performance, open-weight language ... |
| `openai-gpt-oss-20b` | OpenAI-GPT-OSS-20B | 128k | - | - | - | - | 👁️ | GPT-OSS-20B is a compact, open-weight language model opti... |


## <a id='google'></a>🌐 Google (Gemini / Gemma 系列) (共 17 个)

| Poe Bot ID | 显示名称 | 上下文 | 最大输出 | 输入价格 / 1M | 输出价格 / 1M | 缓存读取 / 1M | 特性 | 描述 |
|---|---|---|---|---|---|---|---|---|
| `gemini-2.5-flash` | Gemini-2.5-Flash | 1.1M | 65k | $0.303 | $2.53 | $0.030 | 🛠️ 🧠 👁️ | Gemini 2.5 Flash builds upon the popular foundation of Go... |
| `gemini-2.5-flash-lite` | Gemini-2.5-Flash-Lite | 1M | 64k | $0.101 | $0.404 | - | 🛠️ 🧠 👁️ | A lightweight Gemini 2.5 Flash reasoning model optimized ... |
| `gemini-2.5-pro` | Gemini-2.5-Pro | 1.1M | 65k | $1.26 | $10.10 | $0.126 | 🛠️ 🧠 👁️ | Gemini 2.5 Pro is Google's advanced model with frontier p... |
| `gemini-3-flash` | Gemini-3-Flash | 1M | 65k | $0.404 | $2.42 | $0.040 | 🛠️ 🧠 👁️ | Building on the reasoning capabilities of Gemini 3 Pro, G... |
| `gemini-3.1-flash-lite` | Gemini-3.1-Flash-Lite | 1M | 65k | $0.253 | $1.52 | - | 🛠️ 🧠 👁️ | Gemini 3.1 Flash Lite Preview is the fastest and cheapest... |
| `gemini-3.1-pro` | Gemini-3.1-Pro | 1M | 65k | $2.02 | $12.12 | $0.202 | 🛠️ 🧠 👁️ | Gemini 3.1 Pro is a state-of-the-art model for complex pr... |
| `gemini-3.5-flash` | Gemini-3.5-Flash | 1M | 65k | $1.52 | $9.09 | $0.151 | 🛠️ 🧠 👁️ | Gemini 3.5 Flash is Google’s latest Flash-family AI model... |
| `gemini-3.5-flash-lite` | Gemini-3.5-Flash-Lite | 1M | - | $0.303 | $2.53 | $0.030 | 🌐 🧠 👁️ | Google’s fastest, most cost-efficient Gemini 3.5 model, b... |
| `gemini-3.6-flash` | Gemini-3.6-Flash | 1M | - | $0.758 | $3.79 | $0.076 | 🌐 🧠 👁️ | Google’s token-efficient workhorse model for coding, know... |
| `gemini-3.7-flash` | Gemini-3.7-Flash | 1M | - | $0.758 | $3.79 | $0.076 | 🌐 🧠 👁️ | Google’s most intelligent workhorse model for coding and ... |
| `gemma-3-27b` | Gemma-3-27B | - | - | - | - | - | 🛠️ 👁️ | Gemma 3 introduces multimodality, supporting vision-langu... |
| `gemma-4-26b-a4b` | Gemma-4-26B-A4B | - | - | $0.131 | $0.404 | - | 👁️ | Gemma 4 26B A4B is built for developers who need scalable... |
| `gemma-4-26b-a4b-el` | Gemma-4-26B-A4B-EL | - | - | $0.051 | $0.293 | $0.025 | 🛠️ 👁️ | Gemma 4 26B A4B is a Google open multimodal model with 25... |
| `gemma-4-31b` | Gemma-4-31B | 262k | 8k | - | - | - | 🛠️ 👁️ | Google's most capable open model, delivering frontier-cla... |
| `gemma-4-31b-n` | Gemma-4-31B-N | - | - | $0.141 | $0.404 | - | 👁️ | Gemma 4 31B is engineered to tackle the most demanding en... |
| `gemma-4-31b-t` | Gemma-4-31B-T | - | - | - | - | - | - | Gemma 4 models are designed to deliver frontier-level per... |
| `pearl-gemma-4-31b` | Pearl-Gemma-4-31B | - | - | - | - | - | - | Gemma 4 31B-it-Pearl is Pearl Research Labs' instruction-... |


## <a id='xai'></a>🚀 xAI (Grok 系列) (共 14 个)

| Poe Bot ID | 显示名称 | 上下文 | 最大输出 | 输入价格 / 1M | 输出价格 / 1M | 缓存读取 / 1M | 特性 | 描述 |
|---|---|---|---|---|---|---|---|---|
| `grok-3` | Grok-3 | 131k | - | $3.03 | $15.15 | $0.758 | 🛠️ | xAI's February 2025 flagship release representing nearly ... |
| `grok-3-mini` | Grok-3-Mini | 131k | - | $0.303 | $0.505 | $0.076 | 🛠️ 🧠 | xAI's February 2025 release with strong performance acros... |
| `grok-4` | Grok-4 | 256k | - | $3.03 | $15.15 | $0.758 | 🛠️ 👁️ | Grok 4 is xAI's latest and most intelligent language mode... |
| `grok-4-fast-non-reasoning` | Grok-4-Fast-Non-Reasoning | 2M | - | $0.202 | $0.505 | $0.051 | 🛠️ 👁️ | Grok 4 Fast Non-Reasoning is designed for fast, efficient... |
| `grok-4-fast-reasoning` | Grok-4-Fast-Reasoning | 2M | - | $0.202 | $0.505 | $0.051 | 🛠️ 👁️ | Grok 4 Fast Reasoning delivers exceptional performance fo... |
| `grok-4.1-fast-non-reasoning` | Grok-4.1-Fast-Non-Reasoning | 2M | - | $0.202 | $0.505 | $0.051 | 🛠️ 👁️ | Grok-4.1-Fast-Non-Reasoning is a streamlined companion to... |
| `grok-4.1-fast-reasoning` | Grok-4.1-Fast-Reasoning | 2M | - | $0.202 | $0.505 | $0.051 | 🛠️ 👁️ | Grok-4.1-Fast-Reasoning is a high-performance version of ... |
| `grok-4.20-multi-agent` | Grok-4.20-Multi-Agent | 128k | - | $1.26 | $2.53 | $0.202 | 🛠️ 🧠 👁️ | Realtime Multi-agent Research enables Grok to orchestrate... |
| `grok-4.3` | Grok-4.3 | 1M | - | $1.26 | $2.53 | $0.202 | 🛠️ 👁️ | Grok-4.3 is a reasoning model from xAI designed for agent... |
| `grok-4.5` | Grok-4.5 | 500k | - | $2.02 | $6.06 | $0.303 | 🛠️ 🌐 🧠 👁️ | SpaceXAI's smartest model with frontier performance on co... |
| `grok-4.6` | Grok-4.6 | 500k | - | $2.02 | $6.06 | $0.505 | 🛠️ 🌐 🧠 👁️ | xAI’s frontier model for long-running agents, interactive... |
| `grok-code-fast-1` | Grok-Code-Fast-1 | 256k | - | $0.202 | $1.52 | $0.020 | 🛠️ | Grok-Code-Fast-1 from xAI is a high-performance, cost-eff... |
| `grok-imagine-image-2` | Grok-Imagine-Image-2 | - | - | - | - | - | - | Grok Imagine Image 2.0 generates images from a text promp... |
| `grok-imgn-video-1.5` | Grok-Imgn-Video-1.5 | - | - | - | - | - | - | Grok Imagine Video 1.5 supports text-to-video, image-to-v... |


## <a id='deepseek'></a>🔍 DeepSeek 系列 (共 17 个)

| Poe Bot ID | 显示名称 | 上下文 | 最大输出 | 输入价格 / 1M | 输出价格 / 1M | 缓存读取 / 1M | 特性 | 描述 |
|---|---|---|---|---|---|---|---|---|
| `deepseek-r1-di` | DeepSeek-R1-DI | 64k | - | - | - | - | - | Top open-source reasoning LLM rivaling OpenAI's o1 model;... |
| `deepseek-r1-n` | DeepSeek-R1-N | - | - | - | - | - | 🛠️ | DeepSeek R1 0528 is the latest open-source model released... |
| `deepseek-r1-turbo-di` | DeepSeek-R1-Turbo-DI | 32k | - | - | - | - | - | Top open-source reasoning LLM rivaling OpenAI's o1 model;... |
| `deepseek-v3` | DeepSeek-V3 | - | - | $0.273 | $1.13 | $0.136 | 🛠️ | DeepSeek V3 is DeepSeek's mixture-of-experts flagship cha... |
| `deepseek-v3-di` | DeepSeek-V3-DI | 64k | - | - | - | - | - | Deepseek-v3 – the new top open-source LLM. Achieves state... |
| `deepseek-v3-turbo-di` | DeepSeek-V3-Turbo-DI | 32k | - | - | - | - | - | Deepseek-v3 – the new top open-source LLM. Achieves state... |
| `deepseek-v3.1` | DeepSeek-v3.1 | - | - | $0.212 | $0.798 | - | 🛠️ | DeepSeek V3.1 is a long-context model for coding, tool us... |
| `deepseek-v3.1-terminus` | DeepSeek-V3.1-Terminus | - | - | $0.273 | $1.01 | $0.136 | 🛠️ | DeepSeek V3.1 Terminus is DeepSeek's refined V3.1 model f... |
| `deepseek-v3.2` | DeepSeek-V3.2 | - | - | $0.283 | $0.424 | $0.136 | 🛠️ | DeepSeek V3.2 is DeepSeek's efficient model for long-cont... |
| `deepseek-v3.2-el` | DeepSeek-V3.2-EL | - | - | $0.576 | $1.73 | - | 🛠️ | This model is retiring on 2026-10-10. Please switch to: h... |
| `deepseek-v3.2-exp` | DeepSeek-V3.2-Exp | 160k | - | - | - | - | 🛠️ | DeepSeek-V3.2-Exp is an experimental model introducing th... |
| `deepseek-v4-flash` | DeepSeek-V4-Flash | - | - | $0.141 | $0.283 | $0.028 | 🛠️ | DeepSeek V4 Flash is a text model in DeepSeek’s V4 family... |
| `deepseek-v4-flash-e` | DeepSeek-V4-Flash-E | - | - | $0.202 | $0.404 | - | 🛠️ | DeepSeek V4 Flash is a highly efficient lightweight Mixtu... |
| `deepseek-v4-pro` | DeepSeek-V4-Pro | - | - | $1.76 | $3.52 | $0.146 | 🛠️ | DeepSeek V4 Pro is DeepSeek’s text model with long-contex... |
| `deepseek-v4-pro-0813-el` | DeepSeek-V4-Pro-0813-EL | - | - | $1.33 | $4.00 | - | 🛠️ | DeepSeek V4 Pro 0813 is the official DeepSeek Pro release... |
| `deepseek-v4-pro-e` | DeepSeek-V4-Pro-E | - | - | $2.42 | $4.85 | - | 🛠️ | DeepSeek V4 Pro is a flagship Mixture-of-Experts large la... |
| `deepseek-v4-pro-t` | DeepSeek-V4-Pro-T | - | - | - | - | - | - | DeepSeek V4 Pro is DeepSeek's 1.6T parameter (49B activat... |


## <a id='meta'></a>🦙 Meta (Llama 系列) (共 5 个)

| Poe Bot ID | 显示名称 | 上下文 | 最大输出 | 输入价格 / 1M | 输出价格 / 1M | 缓存读取 / 1M | 特性 | 描述 |
|---|---|---|---|---|---|---|---|---|
| `llama-3.1-8b-di` | Llama-3.1-8B-DI | 128k | - | - | - | - | - | The smallest and fastest model from Meta's Llama 3.1 fami... |
| `llama-3.1-8b-fp16` | Llama-3.1-8B-FP16 | 131k | - | - | - | - | - | The smallest and fastest member of the Llama 3.1 family, ... |
| `llama-3.3-70b-n` | Llama-3.3-70B-N | - | - | - | - | - | 🛠️ | The Meta Llama 3.3 multilingual large language model (LLM... |
| `llama-3.3-70b-t` | Llama-3.3-70B-T | 131k | - | - | - | - | - | Llama 3.3 70B – with similar performance as Llama 3.1 405... |
| `muse-spark-1-1` | Muse-Spark-1.1 | - | - | $1.26 | $4.29 | $0.151 | 🛠️ 🌐 🧠 👁️ | Muse Spark 1.1 is the first model in Meta Superintelligen... |


## <a id='阿里'></a>🇨🇳 阿里 (Qwen / 通义千问 系列) (共 32 个)

| Poe Bot ID | 显示名称 | 上下文 | 最大输出 | 输入价格 / 1M | 输出价格 / 1M | 缓存读取 / 1M | 特性 | 描述 |
|---|---|---|---|---|---|---|---|---|
| `qwen-2.5-7b-t` | Qwen-2.5-7B-T | 32k | - | - | - | - | - | Qwen 2.5 7B from Alibaba. Excels in coding, math, instruc... |
| `qwen-image-2` | Qwen-Image-2 | - | - | - | - | - | - | Qwen-Image-2 is Alibaba's latest image generation model. ... |
| `qwen-image-2-pro` | Qwen-Image-2-Pro | - | - | - | - | - | - | Qwen-Image-2-Pro is Alibaba's latest image generation mod... |
| `qwen-image-3.0-el` | Qwen-Image-3.0-EL | - | - | - | - | - | - | Qwen Image 3.0 supports image generation and editing with... |
| `qwen3-235b-a22b-di` | Qwen3-235B-A22B-DI | 32k | - | - | - | - | - | Qwen3 is the latest generation of large language models i... |
| `qwen3-235b-a22b-n` | Qwen3-235B-A22B-N | - | - | - | - | - | 🛠️ | Qwen3-235B-A22B-Instruct-2507 is a multilingual, instruct... |
| `qwen3-coder-480b-n` | Qwen3-Coder-480B-N | - | - | - | - | - | 🛠️ | Qwen3-Coder-480B-A35B-Instruct is a cutting-edge open cod... |
| `qwen3-coder-next-n` | Qwen3-Coder-Next-N | - | - | $0.202 | $1.52 | - | 🛠️ | Qwen3-Coder-Next is an open-weight language model specifi... |
| `qwen3-max-el` | Qwen3-Max-EL | - | - | $1.09 | $5.58 | - | 🛠️ | This model is retiring on 2026-10-10. Please switch to: h... |
| `qwen3-max-n` | Qwen3-Max-N | - | - | $2.13 | $8.54 | - | 🛠️ | Qwen/qwen3-max, Enhanced with specialized upgrades in age... |
| `qwen3-max-preview-el` | Qwen3-Max-Preview-EL | - | - | $1.09 | $4.85 | - | - | This model is retiring on 2026-10-10. Please switch to: h... |
| `qwen3-max-thinking-el` | Qwen3-Max-Thinking-EL | - | - | $1.09 | $5.58 | - | 🛠️ | This model is retiring on 2026-10-10. Please switch to: h... |
| `qwen3-next-80b` | Qwen3-Next-80B | - | - | $0.151 | $1.52 | - | 🛠️ | Qwen3-Next uses a highly sparse MoE design: 80B total par... |
| `qwen3-next-80b-think` | Qwen3-Next-80B-Think | - | - | $0.151 | $1.52 | - | 🛠️ | Qwen3-Next uses a highly sparse MoE design: 80B total par... |
| `qwen3-vl-235b-a22b-i` | Qwen3-VL-235B-A22B-I | - | - | $0.303 | $1.52 | - | 🛠️ 👁️ | qwen/qwen3-vl-235b-a22b-instruct powered by Novita AI  Fi... |
| `qwen3-vl-235b-a22b-t` | Qwen3-VL-235B-A22B-T | - | - | $0.990 | $3.99 | - | 🛠️ 👁️ | qwen/qwen3-vl-235b-a22b-thinking powered by Novita AI  Fi... |
| `qwen3.5-397b-a17b` | Qwen3.5-397B-A17B | - | - | $0.606 | $3.64 | - | 🛠️ 👁️ | The Qwen3.5 series 397B-A17B native vision-language model... |
| `qwen3.5-4b-el` | Qwen3.5-4B-EL | - | - | $0.040 | $0.071 | $0.020 | 🛠️ 👁️ | Qwen3.5 4B is a low-cost multimodal reasoning model with ... |
| `qwen3.5-9b-el` | Qwen3.5-9B-EL | - | - | $0.091 | $0.131 | $0.045 | 🛠️ 👁️ | Qwen3.5 9B is a compact multimodal reasoning model with 2... |
| `qwen3.5-flash-el` | Qwen3.5-Flash-EL | - | - | $0.091 | $0.372 | - | 🛠️ 👁️ | The Qwen3.5 native vision-language Flash models are built... |
| `qwen3.5-omni-flash` | Qwen3.5-Omni-Flash | - | - | - | - | - | - | Qwen3.5-Omni Flash is the cost-efficient variant of Qwen'... |
| `qwen3.5-omni-plus` | Qwen3.5-Omni-Plus | - | - | - | - | - | - | Qwen3.5-Omni Plus is the flagship variant of Qwen's lates... |
| `qwen3.5-plus-el` | Qwen3.5-Plus-EL | - | - | $0.364 | $2.23 | - | 🛠️ 👁️ | Qwen3.5-Plus is a state-of-the-art multimodal model featu... |
| `qwen3.6-max-preview` | Qwen3.6-Max-Preview | - | - | $1.31 | $7.88 | - | 🛠️ | This model is retiring on 2026-10-10. Please switch to: h... |
| `qwen3.6-plus` | Qwen3.6-Plus | - | - | $0.505 | $3.03 | $0.101 | 🛠️ 👁️ | Qwen 3.6 Plus is Alibaba's 1M-context vision and reasonin... |
| `qwen3.6-plus-t` | Qwen3.6-Plus-T | - | - | - | - | - | - | Qwen3.6-Plus is Qwen's multimodal agentic model built on ... |
| `qwen3.7-flash-el` | Qwen3.7-Flash-EL | - | - | $0.030 | $0.131 | $0.0061 | 🛠️ 👁️ | Qwen3.7 Flash is a fast vision-language model for text, i... |
| `qwen3.7-max-el` | Qwen3.7-Max-EL | - | - | $2.53 | $7.58 | - | 🛠️ | Qwen3.7 Max is a next‑generation flagship model designed ... |
| `qwen3.7-max-t` | Qwen3.7-Max-T | - | - | - | - | - | - | Qwen3.7-Max is Qwen's flagship proprietary model built fo... |
| `qwen3.7-plus` | Qwen3.7-Plus | - | - | $0.404 | $1.62 | $0.081 | 🛠️ 👁️ | Qwen 3.7 Plus is Alibaba's multimodal model for reasoning... |
| `qwen3.8-27b-el` | Qwen3.8-27B-EL | - | - | - | - | - | 🛠️ 🧠 👁️ | Qwen3.8 27B is Alibaba's open multimodal reasoner. It acc... |
| `qwen3.8-max-el` | Qwen3.8-Max-EL | - | - | $2.02 | $6.06 | - | 🛠️ 👁️ | Qwen3.8 Max is Alibaba's flagship Qwen3.8 model, a trilli... |


## <a id='mistral'></a>🌪️ Mistral AI 系列 (共 9 个)

| Poe Bot ID | 显示名称 | 上下文 | 最大输出 | 输入价格 / 1M | 输出价格 / 1M | 缓存读取 / 1M | 特性 | 描述 |
|---|---|---|---|---|---|---|---|---|
| `mistral-7b-v0.3-di` | Mistral-7B-v0.3-DI | 32k | - | - | - | - | - | Mistral Instruct 7B v0.3 from Mistral AI.  All data you p... |
| `mistral-large-2` | Mistral-Large-2 | 128k | 4k | $3.03 | $9.09 | - | 👁️ | Mistral's latest text generation model (Mistral-Large-240... |
| `mistral-medium` | Mistral-Medium | 128k | 4k | $2.73 | $8.18 | - | 👁️ | Mistral AI's medium-sized model. Supports a context windo... |
| `mistral-medium-3` | Mistral-Medium-3 | - | - | - | - | - | 🛠️ 👁️ | This model is retiring on 2026-08-31. Please switch to: h... |
| `mistral-medium-3.1` | Mistral-Medium-3.1 | - | - | $0.525 | $2.63 | - | 🛠️ 👁️ | This model is retiring on 2026-08-31. Please switch to: h... |
| `mistral-small-3` | Mistral-Small-3 | 128k | 4k | $0.101 | $0.303 | - | 👁️ | Mistral Small 3 is a pre-trained and instructed model cat... |
| `mistral-small-3.1` | Mistral-Small-3.1 | - | - | - | - | - | 🛠️ 👁️ | Mistral Small 3.1 24B Instruct is an upgraded variant of ... |
| `mistral-small-4` | Mistral-Small-4 | - | - | - | - | - | 🧠 | Mistral Small 4 is a powerful hybrid model capable of act... |
| `mixtral8x22b-inst-fw` | Mixtral8x22b-Inst-FW | 65k | - | - | - | - | - | Mixtral 8x22B Mixture-of-Experts instruct model from Mist... |


## <a id='图像生成模型'></a>🎨 图像生成模型 (Image Generation) (共 52 个)

| Poe Bot ID | 显示名称 | 厂商 | 生图价格 (Per Image) | 单次请求费 | 特性 | 描述 |
|---|---|---|---|---|---|---|
| `amazon-nova-canvas` | Amazon-Nova-Canvas | EmpirioLabs AI | - | - | - | Note: This model will be retired on September 30, 2026 Amazon Nova Canvas is ... |
| `bria-eraser` | Bria-Eraser | fal | - | - | - | Bria Eraser enables precise removal of unwanted objects from images while mai... |
| `clarity-upscaler` | Clarity-Upscaler | fal | - | - | - | Upscales images with high fidelity to the original image.   Optional paramete... |
| `dreamina-3.1` | Dreamina-3.1 | Bytedance | - | - | - | ByteDance's Dreamina 3.1 Text-to-Image showcases superior picture effects, wi... |
| `flux-2-dev` | FLUX-2-Dev | fal | - | - | - | Open-weight image gen (32B) model, derived from the FLUX.2 base model. The mo... |
| `flux-2-flash` | Flux-2-Flash | fal | - | - | - | Superfast Open-weight image gen (at 32B parameters) model, derived from the F... |
| `flux-2-flex` | FLUX-2-Flex | fal | - | - | - | Flux.2 [Flex] is Black Forest Lab's latest model, with Multi-Reference Suppor... |
| `flux-2-klein-4b` | Flux-2-Klein-4B | fal | - | - | - | Text-to-image generation and Image Editing with Flux 2 [klein] 4B Distilled f... |
| `flux-2-klein-4b-base` | Flux-2-Klein-4B-Base | fal | - | - | - | Text-to-image generation and image editing with Flux 2 [klein] 4B Base from B... |
| `flux-2-klein-9b-base` | Flux-2-Klein-9B-Base | fal | - | - | - | Text-to-image generation and image editing with Flux 2 [klein] 9B Base from B... |
| `flux-2-max` | Flux-2-Max | fal | - | - | - | Flux.2 [Max] is Black Forest Labs' latest, state-of-the-art model with multi-... |
| `flux-2-pro` | FLUX-2-Pro | fal | - | - | - | Flux.2 [Pro] is Black Forest Labs' state-of-the-art model with multi-referenc... |
| `flux-2-turbo` | Flux-2-Turbo | fal | - | - | - | Fast, open-weight image generation model (32B parameters), derived from the F... |
| `flux-dev-finetuner` | FLUX-dev-finetuner | fal | - | - | - | Fine-tune the FLUX dev model with your own pictures! Upload 8-12 of them (sam... |
| `flux-fill` | FLUX-Fill | fal | - | - | - | Given an image and a mask (separate images), fills in the region of the image... |
| `flux-inpaint` | FLUX-Inpaint | fal | - | - | - | Given an image and a mask (separate images), fills in the region of the image... |
| `flux-kontext-max` | Flux-Kontext-Max | fal | - | - | - | FLUX.1 Kontext [max] is a new premium model from Black Forest Labs that bring... |
| `flux-kontext-pro` | Flux-Kontext-Pro | fal | - | - | - | The FLUX.1 Kontext [pro] model delivers state-of-the-art image generation res... |
| `flux-krea` | FLUX-Krea | fal | - | - | - | FLUX-Krea is a version of FLUX Dev tuned for superior aesthetics.   Optional ... |
| `flux-pro-1.1-t` | FLUX-pro-1.1-T | Together AI | - | $0.0300 | - | The best state of the art image model from BFL. FLUX 1.1 Pro generates images... |
| `flux-schnell-t` | Flux-Schnell-T | Together AI | - | $0.0021 | - | Lightning-fast AI image generation model that excels in producing high-qualit... |
| `gpt-image-1` | GPT-Image-1 | OpenAI | - | - | - | OpenAI's model that powers image generation in ChatGPT, offering exceptional ... |
| `gpt-image-1-mini` | GPT-Image-1-Mini | OpenAI | - | - | - | OpenAI's model that powers image generation in ChatGPT, offering exceptional ... |
| `gpt-image-1.5` | GPT-Image-1.5 | OpenAI | - | - | - | OpenAI's frontier image generation model in ChatGPT as of December 2025, offe... |
| `gpt-image-2` | GPT-Image-2 | OpenAI | - | - | - | OpenAI’s state-of-the-art image generation model as of April 21, 2026, design... |
| `grok-imagine-image` | Grok-Imagine-Image | fal | - | - | - | Create creative and artistic images with Grok Imagine Image. Supports text-to... |
| `hunyuan-image-3` | Hunyuan-Image-3 | EmpirioLabs AI | - | - | - | Hunyuan Image 3.0 is Tencent’s next‑generation open‑source text-to-image mode... |
| `ideogram-v2` | Ideogram-v2 | IdeogramAI | - | $0.0580 | - | Latest image model from Ideogram, with industry leading capabilities in gener... |
| `ideogram-v2a` | Ideogram-v2a | IdeogramAI | - | $0.0390 | - | Fast, affordable text-to-image model, optimized for graphic design and photog... |
| `ideogram-v3` | Ideogram-v3 | fal | - | - | - | Generate high-quality images, posters, and logos with Ideogram V3. Features e... |
| `luma-photon` | Luma-Photon | fal | - | - | - | Luma Photon delivers industry-specific visual excellence, crafting images tha... |
| `luma-photon-flash` | Luma-Photon-Flash | fal | - | - | - | Luma Photon delivers industry-specific visual excellence, crafting images tha... |
| `nano-banana` | Nano-Banana | Google | $0.0000 | - | - | Google DeepMind's Nano Banana (i.e. Gemini 2.5 Flash Image model) offers imag... |
| `nano-banana-2` | Nano-Banana-2 | Google | $0.0001 | - | - | Google's latest image model combines Pro-level intelligence with lightning-fa... |
| `nano-banana-2-lite` | Nano-Banana-2-Lite | Google | $0.0000 | - | - | Google's fastest, most efficient Gemini Image model, delivering high-speed ge... |
| `nano-banana-pro` | Nano-Banana-Pro | Google | $0.0001 | - | - | Nano Banana Pro (Gemini 3 Pro Image Preview) can make detailed, context-rich ... |
| `qwen-edit` | Qwen-Edit | fal | - | - | - | Image editing model based on Qwen-Image, with superior text editing capabilit... |
| `remove-background` | remove-background | fal | - | - | - | Remove background from your images |
| `retro-diffusion-core` | Retro-Diffusion-Core | Retro Diffusion | - | - | - | Generate true game ready pixel art in seconds at any resolution between 16x16... |
| `seededit-3.0` | SeedEdit-3.0 | Bytedance | - | - | - | SeedEdit 3.0 is an image editing model independently developed by ByteDance. ... |
| `seedream-3.0` | Seedream-3.0 | Bytedance | - | - | - | Seedream 3.0 by ByteDance is a bilingual (Chinese and English) text-to-image ... |
| `seedream-4.0` | Seedream-4.0 | Bytedance | - | - | - | Seedream 4.0 is ByteDance's latest and best text-to-image model, capable of i... |
| `seedream-4.5` | Seedream-4.5 | Bytedance | - | - | - | Seedream-4.5 is ByteDance's latest and best text-to-image model, capable of i... |
| `seedream-5.0-lite` | Seedream-5.0-Lite | Bytedance | - | - | - | Seedream 5.0 Lite is ByteDance's latest text-to-image model with greater inte... |
| `seedream-5.0-lite-el` | Seedream-5.0-Lite-EL | EmpirioLabs AI | - | - | - | Seedream 5.0 Lite is ByteDance’s unified multimodal image-generation model, d... |
| `seedream-5.0-pro` | Seedream-5.0-Pro | EmpirioLabs AI | - | - | - | Seedream 5.0 Pro creates premium images from text prompts and reference image... |
| `sketch-to-image` | Sketch-to-Image | fal | - | - | - | Takes in sketches and converts them to colored images. |
| `stablediffusion3-2b` | StableDiffusion3-2B | fal | - | - | - | Stable Diffusion v3 Medium - by fal.ai |
| `stablediffusion3.5-l` | StableDiffusion3.5-L | fal | - | - | - | Stability.ai's StableDiffusion3.5 Large, hosted by @fal, is the Stable Diffus... |
| `trellis-3d` | Trellis-3D | fal | - | - | - | Generate 3D models from your images using Trellis, a native 3D generative mod... |
| `wan2.7-image` | Wan2.7-Image | EmpirioLabs AI | - | - | - | Wan2.7 Image is Alibaba's Wan 2.7 series image generation and editing model, ... |
| `z-image-lightning` | Z-Image-Lightning | fal | - | - | - | Super-fast endpoint for Z-Image Turbo, hosted by fal.ai. Excels at portrait p... |


## <a id='音视频与专用工具模型'></a>🎵 音视频与专用工具模型 (Audio / Video / Embeddings) (共 71 个)

| Poe Bot ID | 显示名称 | 上下文 | 最大输出 | 输入价格 / 1M | 输出价格 / 1M | 缓存读取 / 1M | 特性 | 描述 |
|---|---|---|---|---|---|---|---|---|
| `amazon-nova-reel-1.1` | Amazon-Nova-Reel-1.1 | - | - | - | - | - | - | Amazon Nova Reel 1.1 is an advanced AI video generation m... |
| `cartesia-ink-whisper` | Cartesia-Ink-Whisper | - | - | - | - | - | - | Transcribe audio files using Speech-to-Text with the Cart... |
| `elevenlabs-music` | ElevenLabs-Music | 2k | - | - | - | - | - | The ElevenLabs music model is a generative AI system desi... |
| `elevenlabs-music-v2` | ElevenLabs-Music-v2 | - | - | - | - | - | - | ElevenLabs Music v2 is an advanced AI music generation mo... |
| `elevenlabs-v2.5-turbo` | ElevenLabs-v2.5-Turbo | 128k | - | - | - | - | - | ElevenLabs' leading text-to-speech technology converts yo... |
| `elevenlabs-v3` | ElevenLabs-v3 | 128k | - | - | - | - | - | ElevenLabs v3 is a cutting-edge text-to-speech model that... |
| `gemini-2.5-flash-tts` | Gemini-2.5-Flash-TTS | - | - | - | - | - | - | Gemini‑2.5‑Flash‑TTS is Google’s low‐latency text‑to‑spee... |
| `gemini-2.5-pro-tts` | Gemini-2.5-Pro-TTS | - | - | - | - | - | - | Gemini‑2.5‑Pro‑TTS is Google’s highest‑quality text‑to‑sp... |
| `gemini-3.1-flash-tts` | Gemini-3.1-Flash-TTS | - | - | - | - | - | - | Gemini 3.1 Flash TTS is Google’s most controllable text-t... |
| `gemini-omni-flash` | Gemini-Omni-Flash | 1M | - | $1.52 | $9.09 | - | 👁️ | Google's Gemini Omni Flash is a high-quality, cost-effici... |
| `gpt-audio` | GPT-Audio | - | - | - | - | - | - | OpenAI's gpt-audio model, brought to Poe as a server bot!... |
| `gpt-audio-1.5` | GPT-Audio-1.5 | - | - | - | - | - | - | OpenAI's gpt-audio-1.5 model, brought to Poe as a server ... |
| `gpt-audio-mini` | GPT-Audio-Mini | - | - | - | - | - | - | OpenAI's gpt-audio-mini model, brought to Poe as a server... |
| `grok-imagine-video` | Grok-Imagine-Video | 256 | - | - | - | - | 👁️ | Create artistic and creative videos with Grok Imagine Vid... |
| `hailuo-02-pro` | Hailuo-02-Pro | - | - | - | - | - | - | MiniMax Hailuo-02 Pro Video Generation model: Advanced im... |
| `hailuo-02-standard` | Hailuo-02-Standard | - | - | - | - | - | - | MiniMax Hailuo-02 Video Generation model: Advanced image-... |
| `hailuo-ai` | Hailuo-AI | - | - | - | - | - | - | Best-in-class text and image to video model by MiniMax. |
| `hailuo-director-01` | Hailuo-Director-01 | - | - | - | - | - | - | Generate video clips more accurately with respect to natu... |
| `hailuo-music-v1.5` | Hailuo-Music-v1.5 | - | - | - | - | - | - | Generate music from text prompts using the MiniMax model,... |
| `inkling` | Inkling | 256k | - | $1.01 | $4.09 | $0.172 | 🧠 👁️ | Inkling is Thinking Machines’ multimodal reasoning model,... |
| `kling-1.5-pro` | Kling-1.5-Pro | - | - | - | - | - | 👁️ | Kling-1.5-Pro video generation bot, hosted by fal.ai. For... |
| `kling-2.0-master` | Kling-2.0-Master | - | - | - | - | - | - | Generate high-quality videos from text or images using Kl... |
| `kling-2.1-pro` | Kling-2.1-Pro | - | - | - | - | - | - | Kling 2.1 Pro is an advanced endpoint for the Kling 2.1 m... |
| `kling-2.1-std` | Kling-2.1-Std | - | - | - | - | - | - | Kling 2.1 Standard is a cost-efficient endpoint for the K... |
| `kling-2.5-turbo-pro` | Kling-2.5-Turbo-Pro | - | - | - | - | - | - | Generate high-quality videos from text and images using K... |
| `kling-2.5-turbo-std` | Kling-2.5-Turbo-Std | - | - | - | - | - | 👁️ | Generate high-quality videos from images using Kling 2.5 ... |
| `kling-2.6-pro` | Kling-2.6-Pro | 256 | - | - | - | - | - | Generate high-quality videos with native audio from text ... |
| `kling-3.0-turbo` | Kling-3.0-Turbo | - | - | - | - | - | - | Kling 3.0 Turbo is a fast video generation model that pro... |
| `kling-avatar-pro` | Kling-Avatar-Pro | - | - | - | - | - | 👁️ | Create lifelike avatar videos featuring realistic humans,... |
| `kling-o3` | Kling-O3 | 256 | - | - | - | - | 👁️ | Kling O3 is a versatile AI video generation model capable... |
| `kling-omni` | Kling-Omni | - | - | - | - | - | 👁️ | Bot for Kling Omni Image-to-Video inference. Send one ima... |
| `kling-pro-effects` | Kling-Pro-Effects | - | - | - | - | - | - | Generate videos with effects like squishing an object, tw... |
| `kling-v3-motion-ctrl` | Kling-v3-Motion-Ctrl | - | - | - | - | - | - | Kling v3 Motion Control uses Kuaishou's Kling 3.0 model t... |
| `kling-v3-pro` | Kling-v3-Pro | 256 | - | - | - | - | - | Kling v3 Pro Video bot, capable of text to video and imag... |
| `ltx-2-fast` | LTX-2-Fast | - | - | - | - | - | 👁️ | LTX-2 Fast is a video model by Lightricks that delivers e... |
| `ltx-2-pro` | LTX-2-Pro | - | - | - | - | - | 👁️ | LTX-2 Pro is an advanced video generation model by Lightr... |
| `lyria` | Lyria | - | - | - | - | - | - | Google DeepMind's Lyria 2 delivers high-quality audio gen... |
| `lyria-3` | Lyria-3 | - | - | - | - | - | - | Google DeepMind’s Lyria 3 is an advanced AI music generat... |
| `minimax-speech-2.8` | MiniMax-Speech-2.8 | - | - | - | - | - | - | MiniMax Speech 2.8 is a premium text-to-speech model deli... |
| `moss-video-and-audio` | MOSS-Video-and-Audio | - | - | - | - | - | - | MOSS Video and Audio (MOVA) is an open-source foundation ... |
| `omnihuman` | OmniHuman | - | - | - | - | - | - | OmniHuman, by Bytedance, generates video using an image o... |
| `orpheus-tts` | Orpheus-TTS | - | - | - | - | - | - | Orpheus TTS is a state-of-the-art, Llama-based Speech-LLM... |
| `pixverse-v4.5` | Pixverse-v4.5 | - | - | - | - | - | - | Pixverse v4.5 is a video generation model capable of gene... |
| `pixverse-v5` | Pixverse-v5 | - | - | - | - | - | - | Pixverse v5 offers advanced creative tools with three mai... |
| `pixverse-v5.6` | Pixverse-v5.6 | - | - | - | - | - | - | PixVerse v5.6 is capable of creating high-quality videos ... |
| `qwen-audio-3.0-tts` | Qwen-Audio-3.0-TTS | - | - | - | - | - | - | Qwen Audio 3.0 TTS is Alibaba's speech synthesis model, a... |
| `runway-gen-4.5` | Runway-Gen-4.5 | 256 | - | - | - | - | - | Runway Gen 4.5 is an advanced video model that generates ... |
| `seedance-1.0-lite` | Seedance-1.0-Lite | - | - | - | - | - | - | Seedance is a video generation model with text-to-video a... |
| `seedance-1.0-pro` | Seedance-1.0-Pro | - | - | - | - | - | - | Seedance is a video generation model with text-to-video a... |
| `seedance-1.0-pro-fast` | Seedance-1.0-Pro-Fast | - | - | - | - | - | 👁️ | Seedance Pro Fast is a faster version of Seedance 1.0 Pro... |
| `seedance-2-fast` | Seedance-2-Fast | - | - | - | - | - | - | Seedance 2.0 Fast supports the text and image inputs but ... |
| `seedance-2.0` | Seedance-2.0 | - | - | - | - | - | - | Seedance 2.0 delivers high‑quality video generation acros... |
| `seedance-2.0-fast-el` | Seedance-2.0-Fast-EL | - | - | - | - | - | - | Seedance 2.0 Fast is the speed-optimized version of Seeda... |
| `seedance-2.0-pro-el` | Seedance-2.0-Pro-EL | - | - | - | - | - | - | Seedance 2.0 Pro is a multimodal AI video generation mode... |
| `sora-2` | Sora-2 | 480 | - | - | - | - | 👁️ | Sora 2 is OpenAI’s latest video and audio generation mode... |
| `sora-2-pro` | Sora-2-Pro | 480 | - | - | - | - | 👁️ | Sora 2 Pro is OpenAI’s state-of-the-art video and audio g... |
| `stable-audio-2.0` | Stable-Audio-2.0 | - | - | - | - | - | - | Stable Audio 2.0 generates audio up to 3 minutes long fro... |
| `stable-audio-2.5` | Stable-Audio-2.5 | - | - | - | - | - | - | Stable Audio 2.5 generates high-quality audio up to 3 min... |
| `svi-2.0-pro` | SVI-2.0-Pro | - | - | - | - | - | - | Stable Video Infinity 2.0 Pro, powered by WAN 2.2, genera... |
| `veo-3-vfast` | Veo-3-vFast | - | - | - | - | - | - | Veo-3 Fast is a faster and more cost effective version of... |
| `veo-3.1` | Veo-3.1 | 480 | - | - | - | - | - | Google’s Veo 3.1 is an updated version of the Veo family ... |
| `veo-3.1-fast` | Veo-3.1-Fast | 480 | - | - | - | - | 👁️ | Google’s Veo 3.1 Fast is an updated version of the Veo fa... |
| `veo-3.1-lite` | Veo-3.1-Lite | 480 | - | - | - | - | 👁️ | Google’s Veo 3.1 Lite is the most cost-efficient model in... |
| `veo-v3.1` | Veo-v3.1 | - | - | - | - | - | - | Google's Veo-3.1 is an improved version of Veo 3.  Option... |
| `veo-v3.1-fast` | Veo-v3.1-Fast | - | - | - | - | - | 👁️ | Google's Veo 3.1 Fast is a fast version of Veo 3.1.  Opti... |
| `vidu` | Vidu | - | - | - | - | - | 👁️ | The Vidu Video Generation Bot creates videos using images... |
| `wan-2.5` | Wan-2.5 | - | - | - | - | - | 👁️ | Wan-2.5 Video Generation bot. Has text-to-video and image... |
| `wan-2.6` | Wan-2.6 | - | - | - | - | - | - | Wan 2.6 is Alibaba’s multimodal video generation model bu... |
| `wan-2.7` | Wan-2.7 | - | - | - | - | - | - | Wan 2.7 is Alibaba's latest multimodal video generation m... |
| `wan-animate` | Wan-Animate | - | - | - | - | - | - | Wan Animate takes in an image and a video to generate ano... |
| `whisper-v3-large-t` | Whisper-V3-Large-T | - | - | - | - | - | - | Whisper v3 Large is a state-of-the-art automatic speech r... |


## <a id='其他主流与社区模型'></a>📦 其他主流与社区模型 (Other / Community Models) (共 77 个)

| Poe Bot ID | 显示名称 | 上下文 | 最大输出 | 输入价格 / 1M | 输出价格 / 1M | 缓存读取 / 1M | 特性 | 描述 |
|---|---|---|---|---|---|---|---|---|
| `assistant` | Assistant | 400k | 128k | - | - | - | 🛠️ 🌐 🧠 👁️ | General-purpose assistant. Write, code, ask for real-time... |
| `canvas-creator` | Canvas-Creator | - | - | - | - | - | - | Specializes in building interactive web applications desi... |
| `code-editor` | Code-Editor | - | - | - | - | - | - | Official code editor for Poe Scripting using Python, used... |
| `code-saver` | Code-Saver | - | - | - | - | - | - | A system bot that handles Poe scripts in chat. |
| `deep-ai-search` | Deep-AI-Search | - | - | - | - | - | - | Deep search engine that integrates Brave AI with real-tim... |
| `deepgram-nova-3` | Deepgram-Nova-3 | - | - | - | - | - | - | Transcribe audio files using Speech-to-Text technology wi... |
| `deepreasoning` | DeepReasoning | - | - | $5.05 | $10.10 | - | - | DeepReasoning (previously DeepClaude) is a high-performan... |
| `ds-v4-flash-0731-el` | DS-V4-Flash-0731-EL | - | - | $0.428 | $1.28 | - | 🛠️ | DeepSeek V4 Flash 0731 is a 284B MoE reasoning model with... |
| `exa-answer` | Exa-Answer | - | - | - | - | - | - | Get a quick LLM-style answer to a question informed by Ex... |
| `exa-search` | Exa-Search | - | - | - | - | - | - | Utilize Exa's technology for searching web pages, finding... |
| `fugu-ultra-v1.0-el` | Fugu-Ultra-v1.0-EL | - | - | $7.58 | $45.45 | $1.52 | 🛠️ 🧠 👁️ | Fugu Ultra v1.0 is Sakana AI's multi-agent conductor: it ... |
| `fugu-ultra-v1.1-el` | Fugu-Ultra-v1.1-EL | - | - | $5.05 | $30.30 | $0.505 | 🛠️ 🧠 👁️ | Fugu Ultra v1.1 is Sakana AI's multi-agent conductor with... |
| `glm-4.6` | GLM-4.6 | - | - | $0.606 | $2.22 | $0.111 | 🛠️ | Z.ai GLM 4.6 is a coding-focused model for large codebase... |
| `glm-4.6v-n` | GLM-4.6V-N | - | - | $0.303 | $0.909 | $0.056 | 🛠️ 👁️ | GLM-4.6V represents a significant multimodal advancement ... |
| `glm-4.7` | GLM-4.7 | - | - | $0.606 | $2.22 | $0.121 | 🛠️ | Z.ai GLM 4.7 improves coding, tool use, and multi-step re... |
| `glm-4.7-flash-n` | GLM-4.7-Flash-N | - | - | $0.071 | $0.404 | $0.010 | 🛠️ | GLM-4.7-Flash, a state-of-the-art model in the 30B class,... |
| `glm-5` | GLM-5 | - | - | $1.01 | $3.23 | $0.202 | 🛠️ | Z.ai GLM 5 supports agentic coding, autonomous tool use, ... |
| `glm-5.1` | GLM-5.1 | - | - | $1.41 | $4.44 | $0.263 | 🛠️ | Z.ai GLM 5.1 is built for long-horizon autonomous coding:... |
| `glm-5.2` | GLM-5.2 | - | - | $1.52 | $4.55 | $0.303 | 🛠️ | GLM 5.2 is Z.AI's flagship open-weight model for long-hor... |
| `happyhorse-1.0-el` | HappyHorse-1.0-EL | - | - | - | - | - | - | HappyHorse 1.0 is a video generation model, capable of cr... |
| `happyhorse-1.1` | HappyHorse-1.1 | - | - | - | - | - | - | HappyHorse 1.1, from Alibaba, supports text-to-video, ima... |
| `hy3` | Hy3 | - | - | $0.141 | $0.586 | $0.035 | 🛠️ | Tencent Hy3 is a reasoning model for coding, tool use, an... |
| `interpreter` | Interpreter | - | - | - | - | - | 👁️ | Interpreter for Poe Python |
| `kimi-k2-thinking` | Kimi-K2-Thinking | - | - | $0.475 | $2.02 | $0.142 | 🛠️ | Moonshot AI Kimi K2 Thinking is a reasoning model for lon... |
| `kimi-k2.5` | Kimi-K2.5 | - | - | $0.606 | $3.03 | $0.101 | 🛠️ 👁️ | Moonshot AI Kimi K2.5 is a multimodal model for visual an... |
| `kimi-k2.6` | Kimi-K2.6 | - | - | $0.960 | $4.04 | $0.162 | 🛠️ 👁️ | Moonshot AI Kimi K2.6 is a model for long-horizon coding,... |
| `kimi-k2.7-code` | Kimi-K2.7-Code | - | - | $0.960 | $4.04 | $0.192 | 🛠️ 👁️ | Moonshot AI Kimi K2.7 Code is a coding model for agent pe... |
| `kimi-k3` | Kimi-K3 | 1M | - | $3.03 | $15.15 | $0.303 | 🛠️ 🧠 👁️ | Kimi’s flagship model for long-horizon coding and end-to-... |
| `kimi-k3-el` | Kimi-K3-EL | - | - | $3.03 | $15.15 | - | 🛠️ 🧠 👁️ | Kimi K3 is Moonshot AI's flagship reasoning model with a ... |
| `linkup-deep-search` | Linkup-Deep-Search | - | - | - | - | - | - | Linkup Deep Search is an AI-powered search bot that conti... |
| `linkup-standard` | Linkup-Standard | - | - | - | - | - | - | Linkup Standard is an AI-powered search bot that provides... |
| `liveportrait` | LivePortrait | - | - | - | - | - | - | Animates given portraits with the motion's in the video. ... |
| `manus` | Manus | - | - | - | - | - | - | Manus is an autonomous AI agent that executes tasks. It c... |
| `markitdown` | MarkItDown | - | - | - | - | - | - | Convert anything to Markdown: URLs, PDFs, Word, Excel, im... |
| `mimo-v2-flash` | MiMo-V2-Flash | - | - | $0.101 | $0.303 | $0.020 | 🛠️ | Xiaomi MiMo-V2-Flash is a proprietary MoE model developed... |
| `mimo-v2.5-el` | MiMo-V2.5-EL | - | - | - | - | - | - | MiMo-V2.5 is a multimodal model with native visual and au... |
| `mimo-v2.5-pro` | MiMo-V2.5-Pro | - | - | $1.01 | $3.03 | $0.202 | 🛠️ | Xiaomi MiMo V2.5 Pro is a reasoning model for agentic wor... |
| `minimax-h3-el` | MiniMax-H3-EL | - | - | - | - | - | - | MiniMax H3 is a multimodal video generation model that pr... |
| `minimax-m2` | MiniMax-M2 | - | - | $0.303 | $1.21 | $0.030 | 🛠️ | MiniMax M2 is a fast, efficient model for coding, agentic... |
| `minimax-m2.1` | MiniMax-M2.1 | - | - | $0.303 | $1.21 | $0.030 | 🛠️ | MiniMax M2.1 is a reasoning model optimized for robust co... |
| `minimax-m2.5` | MiniMax-M2.5 | - | - | $0.273 | $0.960 | $0.030 | 🛠️ | MiniMax M2.5 is a reasoning model for end-to-end developm... |
| `minimax-m2.7` | MiniMax-M2.7 | - | - | $0.303 | $1.21 | $0.061 | 🛠️ | MiniMax M2.7 is a reasoning model for end-to-end software... |
| `minimax-m2.7-fw` | Minimax-M2.7-FW | - | - | - | - | - | 🛠️ | Mixture-of-Experts language model. M2.7 is capable of bui... |
| `minimax-m3` | MiniMax-M3 | - | - | $0.303 | $1.21 | $0.061 | 🛠️ 👁️ | MiniMax M3 is MiniMax's open-weight frontier model for co... |
| `minimax-m3-t` | MiniMax-M3-T | - | - | - | - | - | - | MiniMax M3 is MiniMax's frontier open-weight model combin... |
| `mochi-preview` | Mochi-preview | - | - | - | - | - | - | Open state-of-the-art video generation model with high-fi... |
| `muse-glimmer-30b-el` | Muse-Glimmer-30B-EL | - | - | - | - | - | 🛠️ 🧠 👁️ | Muse Glimmer 30B is Meta's open agentic model, built for ... |
| `nova-lite-1.0` | Nova-Lite-1.0 | - | - | $0.070 | $0.283 | $0.038 | 🛠️ 👁️ | Amazon Nova Lite is a low‑cost multimodal foundation mode... |
| `nova-lite-2` | Nova-Lite-2 | - | - | $0.384 | $3.19 | $0.211 | 🛠️ 🧠 👁️ | Amazon Nova 2 Lite is a fast, cost-effective multimodal r... |
| `nova-micro-1.0` | Nova-Micro-1.0 | - | - | $0.040 | $0.162 | $0.022 | 🛠️ | Amazon Nova Micro is a text-only foundation model in the ... |
| `nova-premier-1.0` | Nova-Premier-1.0 | - | - | $3.03 | $15.15 | $1.67 | 🛠️ 👁️ | Note: This model will be retired on September 14, 2026 Th... |
| `nova-pro-1.0` | Nova-Pro-1.0 | - | - | - | - | - | - | Amazon Nova Pro 1.0 is a highly capable multimodal founda... |
| `perplexity-adv-deep-research` | Perplexity-Adv-Deep-Research | - | - | - | - | - | 🧠 | Perplexity Advanced Deep Research is designed for institu... |
| `perplexity-deep-research` | Perplexity-Deep-Research | 128k | - | - | - | - | 🧠 | Perplexity Deep Research is a research-focused model desi... |
| `perplexity-pro-search` | Perplexity-Pro-Search | - | - | - | - | - | - | Perplexity Pro Search turns Sonar Pro into a full agentic... |
| `perplexity-search` | Perplexity-Search | - | - | - | - | - | - | Utilize Perplexity's technology for real-time web search ... |
| `perplexity-sonar` | Perplexity-Sonar | 127k | - | - | - | - | - | Sonar by Perplexity is a cutting-edge AI model that deliv... |
| `perplexity-sonar-pro` | Perplexity-Sonar-Pro | 200k | - | - | - | - | - | Sonar Pro by Perplexity is an advanced AI model that enha... |
| `perplexity-sonar-rsn-pro` | Perplexity-Sonar-Rsn-Pro | 128k | - | - | - | - | - | This model operates on the open-sourced uncensored R1-177... |
| `phi-4-di` | Phi-4-DI | 16k | - | - | - | - | - | Microsoft Research Phi-4 is designed to perform well in c... |
| `pika-v1.5-effects` | Pika-v1.5-Effects | - | - | - | - | - | - | Apply surprising, mind blowing effects to your photo with... |
| `python` | Python | 131k | - | - | - | - | - | Executes Python code (version 3.11) from the user message... |
| `reka-core` | Reka-Core | 128k | - | - | - | - | - | Reka's largest and most capable multimodal language model... |
| `reka-flash` | Reka-Flash | 128k | - | - | - | - | - | Reka's efficient and capable 21B multimodal model optimiz... |
| `reka-research` | Reka-Research | - | - | - | - | - | - | Reka Research is a state-of-the-art agentic AI that answe... |
| `restyler` | Restyler | - | - | - | - | - | - | This bot enables rapid transformation of existing images,... |
| `script-bot-creator` | Script-Bot-Creator | - | - | - | - | - | - | Specializes in building workflows that combine bots on Po... |
| `seed-2.0-code` | Seed-2.0-Code | - | - | $0.631 | $3.79 | - | 🛠️ 🧠 👁️ | Seed 2.0 Code is optimized for enterprise-grade coding sc... |
| `seed-2.0-lite` | Seed-2.0-Lite | - | - | $0.316 | $2.53 | - | 🛠️ 🧠 👁️ | Seed 2.0 Lite is a balanced model designed for high-frequ... |
| `seed-2.0-mini` | Seed-2.0-Mini | - | - | $0.126 | $0.505 | - | 🛠️ 🧠 👁️ | Seed-2.0-Mini from Bytedance targets latency-sensitive, h... |
| `seed-2.0-pro` | Seed-2.0-Pro | - | - | $0.631 | $3.79 | - | 🛠️ 🧠 👁️ | Seed 2.0 Pro is a flagship all-purpose general model desi... |
| `seed-2.1-turbo` | Seed-2.1-Turbo | - | - | $0.636 | $3.16 | - | 🛠️ 🧠 👁️ | Seed 2.1 Turbo is ByteDance's next-generation coding and ... |
| `seedance-2.0-mini` | Seedance-2.0-Mini | - | - | - | - | - | - | Seedance 2.0 Mini is the fast, low-cost tier of ByteDance... |
| `seedance-2.5-el` | Seedance-2.5-EL | - | - | - | - | - | - | Seedance 2.5 is ByteDance's next-generation video model. ... |
| `solar-pro-2` | Solar-Pro-2 | 4k | 1k | - | - | - | 👁️ | Solar Pro 2 is Upstage's latest frontier-scale LLM. With ... |
| `step-3.7-flash-el` | Step-3.7-Flash-EL | - | - | $0.202 | $1.16 | $0.040 | 🛠️ 🧠 👁️ | StepFun multimodal reasoning model with image and video i... |
| `tako` | Tako | 2k | - | - | - | - | - | Tako is a bot that transforms your questions about stocks... |


## 如何在本项目中配置模型映射

本项目支持通过环境变量 `MODEL_MAPPING` 将任何 OpenAI / 客户端常用模型名称映射到上述任意 Poe Bot ID。

编辑 `.env` 文件中的 `MODEL_MAPPING`（格式为 JSON 键值对）：

```json
MODEL_MAPPING={"gpt-4o":"gpt-4o","claude-3-7-sonnet":"claude-3.7-sonnet","claude-3-7-sonnet-thinking":"claude-3.7-sonnet-thinking","gemini-2.5-pro":"gemini-2.5-pro","deepseek-r1":"deepseek-r1","grok-3":"grok-3","flux-pro":"flux-2-pro"}
```

保存后重启服务即可：
```bash
./start.sh restart
```

---

## 自动更新模型与价格数据

若 Poe 官方上线了新模型或调整了价格，可通过以下方式刷新：

1. **重新获取最新 `models.json`**：
```bash
curl -H "Authorization: Bearer <YOUR_POE_API_KEY>" https://api.poe.com/v1/models > models.json
```

2. **重新生成本 Markdown 文档**：
```bash
python3 generate_models_doc.py
```
