import json
import os
from collections import defaultdict

def format_tokens(num):
    if num is None:
        return "-"
    if num >= 1_000_000:
        return f"{num / 1_000_000:.1f}M".replace(".0M", "M")
    if num >= 1_000:
        return f"{num // 1_000}k"
    return str(num)

def format_price_per_m(val):
    if val is None:
        return "-"
    try:
        f = float(val)
        if f == 0:
            return "Free"
        # Convert to $ / 1M tokens (multiply by 1,000,000)
        per_m = f * 1_000_000
        if per_m >= 1:
            return f"${per_m:.2f}"
        elif per_m >= 0.01:
            return f"${per_m:.3f}"
        else:
            return f"${per_m:.4f}"
    except Exception:
        return str(val)

def format_raw_cost(val):
    if val is None:
        return "-"
    try:
        f = float(val)
        if f == 0:
            return "Free"
        return f"${f:.4f}"
    except Exception:
        return str(val)

def categorize_model(m):
    mid = m.get("id", "").lower()
    owned_by = (m.get("owned_by") or "").lower()
    desc = (m.get("description") or "").lower()
    modalities = m.get("architecture", {}).get("output_modalities", [])
    
    # Image Generation
    if "image" in modalities and "text" not in modalities:
        return "🎨 图像生成模型 (Image Generation)"
    if any(k in mid for k in ["flux", "dall-e", "stable-diffusion", "sdxl", "midjourney", "nano-banana", "seedream", "ideogram", "recraft", "imagen"]):
        return "🎨 图像生成模型 (Image Generation)"
        
    # Video / Audio / Embedding
    if "audio" in modalities or "video" in modalities or any(k in mid for k in ["whisper", "tts", "elevenlabs", "suno", "luma", "runway", "kling", "embed"]):
        return "🎵 音视频与专用工具模型 (Audio / Video / Embeddings)"

    # Anthropic
    if "anthropic" in owned_by or "claude" in mid:
        return "🧠 Anthropic (Claude 系列)"
        
    # OpenAI
    if "openai" in owned_by or any(k in mid for k in ["gpt", "o1", "o3", "chatgpt", "text-embedding"]):
        return "⚡ OpenAI (GPT / o 系列)"
        
    # Google
    if "google" in owned_by or "gemini" in mid or "gemma" in mid:
        return "🌐 Google (Gemini / Gemma 系列)"
        
    # xAI
    if "xai" in owned_by or "grok" in mid:
        return "🚀 xAI (Grok 系列)"
        
    # DeepSeek
    if "deepseek" in owned_by or "deepseek" in mid:
        return "🔍 DeepSeek 系列"
        
    # Meta
    if "meta" in owned_by or "llama" in mid:
        return "🦙 Meta (Llama 系列)"
        
    # Alibaba / Qwen
    if "alibaba" in owned_by or "qwen" in mid or "qwq" in mid:
        return "🇨🇳 阿里 (Qwen / 通义千问 系列)"
        
    # Mistral
    if "mistral" in owned_by or "mistral" in mid or "mixtral" in mid or "codestral" in mid or "pixtral" in mid:
        return "🌪️ Mistral AI 系列"

    return "📦 其他主流与社区模型 (Other / Community Models)"

def generate_markdown():
    with open("models.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    
    models = data.get("data", []) if isinstance(data, dict) else data
    print(f"Total models loaded: {len(models)}")
    
    categories = defaultdict(list)
    for m in models:
        cat = categorize_model(m)
        categories[cat].append(m)
        
    cat_order = [
        "🧠 Anthropic (Claude 系列)",
        "⚡ OpenAI (GPT / o 系列)",
        "🌐 Google (Gemini / Gemma 系列)",
        "🚀 xAI (Grok 系列)",
        "🔍 DeepSeek 系列",
        "🦙 Meta (Llama 系列)",
        "🇨🇳 阿里 (Qwen / 通义千问 系列)",
        "🌪️ Mistral AI 系列",
        "🎨 图像生成模型 (Image Generation)",
        "🎵 音视频与专用工具模型 (Audio / Video / Embeddings)",
        "📦 其他主流与社区模型 (Other / Community Models)"
    ]
    
    lines = []
    lines.append("# Poe 可用模型与定价一览表 (Poe Models & Pricing Catalog)\n")
    lines.append("> **说明**：数据来自 Poe 官方 API `/v1/models` 响应，涵盖全部 **" + str(len(models)) + "** 个官方及热门模型。")
    lines.append("> - **输入/输出定价**：换算为 **$ / 1M Tokens**（每百万 Tokens 美元价格），方便与各官方 API 直观比对。")
    lines.append("> - **图像生成定价**：标注为 **$/张 (Per Image)** 或单次点数。")
    lines.append("> - **特性标记**：🛠️ 支持工具/函数调用 (Tools) ｜ 🌐 支持联网搜索 (Web Search) ｜ 🧠 支持思考推理 (Reasoning) ｜ 👁️ 支持多模态视觉 (Vision)。")
    lines.append("> - **在项目中使用**：只需在 `.env` 的 `MODEL_MAPPING` 中将客户端请求的模型名称映射到对应的 **Poe Bot ID** 即可。\n")
    
    lines.append("## 目录 (Table of Contents)\n")
    for cat in cat_order:
        if cat in categories and categories[cat]:
            anchor = cat.split(" ")[1].lower().replace("/", "").replace("(", "").replace(")", "").replace(" ", "-")
            lines.append(f"- [{cat}](#{anchor}) （共 {len(categories[cat])} 个）")
    lines.append("- [如何在本项目中配置模型映射](#如何在本项目中配置模型映射)")
    lines.append("- [自动更新模型与价格数据](#自动更新模型与价格数据)\n")
    lines.append("---\n")
    
    for cat in cat_order:
        m_list = categories.get(cat, [])
        if not m_list:
            continue
            
        anchor = cat.split(" ")[1].lower().replace("/", "").replace("(", "").replace(")", "").replace(" ", "-")
        lines.append(f"## <a id='{anchor}'></a>{cat} (共 {len(m_list)} 个)\n")
        
        # Check if it's image category
        is_image_cat = "图像" in cat
        
        if is_image_cat:
            lines.append("| Poe Bot ID | 显示名称 | 厂商 | 生图价格 (Per Image) | 单次请求费 | 特性 | 描述 |")
            lines.append("|---|---|---|---|---|---|---|")
            for m in sorted(m_list, key=lambda x: x.get("id", "")):
                mid = m.get("id", "")
                meta = m.get("metadata") or {}
                dname = meta.get("display_name") or mid
                vendor = m.get("owned_by") or "-"
                pricing = m.get("pricing") or {}
                img_price = format_raw_cost(pricing.get("image"))
                req_price = format_raw_cost(pricing.get("request"))
                
                features = []
                feats = m.get("supported_features") or []
                if "tools" in feats: features.append("🛠️")
                if "web_search" in feats: features.append("🌐")
                feat_str = " ".join(features) if features else "-"
                
                desc = (m.get("description") or "").replace("\n", " ").replace("|", "/")
                if len(desc) > 80:
                    desc = desc[:77] + "..."
                    
                lines.append(f"| `{mid}` | {dname} | {vendor} | {img_price} | {req_price} | {feat_str} | {desc} |")
        else:
            lines.append("| Poe Bot ID | 显示名称 | 上下文 | 最大输出 | 输入价格 / 1M | 输出价格 / 1M | 缓存读取 / 1M | 特性 | 描述 |")
            lines.append("|---|---|---|---|---|---|---|---|---|")
            for m in sorted(m_list, key=lambda x: x.get("id", "")):
                mid = m.get("id", "")
                meta = m.get("metadata") or {}
                dname = meta.get("display_name") or mid
                
                ctx_obj = m.get("context_window") or {}
                ctx_len = ctx_obj.get("context_length") or m.get("context_length")
                max_out = ctx_obj.get("max_output_tokens")
                ctx_str = format_tokens(ctx_len)
                max_out_str = format_tokens(max_out)
                
                pricing = m.get("pricing") or {}
                p_in = format_price_per_m(pricing.get("prompt"))
                p_out = format_price_per_m(pricing.get("completion"))
                p_cache = format_price_per_m(pricing.get("input_cache_read"))
                
                features = []
                feats = m.get("supported_features") or []
                arch = m.get("architecture") or {}
                inputs = arch.get("input_modalities") or []
                if "tools" in feats: features.append("🛠️")
                if "web_search" in feats: features.append("🌐")
                if m.get("reasoning") or any("reasoning" in p.get("name", "") for p in m.get("parameters", [])):
                    features.append("🧠")
                if "image" in inputs:
                    features.append("👁️")
                feat_str = " ".join(features) if features else "-"
                
                desc = (m.get("description") or "").replace("\n", " ").replace("|", "/")
                if len(desc) > 60:
                    desc = desc[:57] + "..."
                if not desc:
                    desc = "-"
                    
                lines.append(f"| `{mid}` | {dname} | {ctx_str} | {max_out_str} | {p_in} | {p_out} | {p_cache} | {feat_str} | {desc} |")
                
        lines.append("\n")
        
    lines.append("""## 如何在本项目中配置模型映射

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
""")

    with open("MODELS.md", "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
        
    print("MODELS.md generated successfully!")

if __name__ == "__main__":
    generate_markdown()