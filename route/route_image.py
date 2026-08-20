import logging
from datetime import datetime

from dotenv import load_dotenv
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from api import poe_api
from util.auth import get_poe_api_key

logger = logging.getLogger(__name__)

router = APIRouter()
load_dotenv()


@router.post("/v1/images/generations")
async def image_generation(request: Request):
    """
    兼容OpenAI的图像生成API
    """
    try:
        body = await request.json()
    except Exception:
        return JSONResponse(status_code=400,
                            content={"error": {"message": "请求体不是合法的 JSON", "type": "invalid_request_error", "code": None}})
    if not isinstance(body, dict):
        return JSONResponse(status_code=400,
                            content={"error": {"message": "请求体必须是 JSON 对象", "type": "invalid_request_error", "code": None}})

    prompt = body.get('prompt', '')
    n = body.get('n', 1)  # OpenAI支持生成多张图片，但Poe目前一次只能生成一张
    size = body.get('size', '1024x1024')  # OpenAI格式的尺寸
    model = body.get('model', 'dall-e-3')  # 默认使用DALL-E-3

    if not prompt:
        return JSONResponse(status_code=400,
                            content={"error": {"message": "prompt 不能为空", "type": "invalid_request_error", "code": None}})

    api_key = get_poe_api_key()
    session = getattr(request.app.state, "http_session", None)

    # 处理提示词和尺寸
    formatted_prompt = format_prompt_with_size(prompt, size)

    try:
        result = await poe_api.get_image(api_key, formatted_prompt, model, session=session)
    except Exception as e:
        logger.error("Poe 图像生成失败: %s: %s", type(e).__name__, e)
        detail = str(e)[:300] or type(e).__name__
        return JSONResponse(status_code=502,
                            content={"error": {"message": f"上游 Poe 请求失败: {detail}", "type": "upstream_error", "code": None}})

    return JSONResponse(content=format_response(result, prompt))


def format_prompt_with_size(prompt, size):
    """
    根据OpenAI的尺寸参数格式化提示词，转换为aspect比例
    """
    # 如果用户在prompt中已经指定了尺寸或宽高比，不再添加
    if "--size" in prompt or "--aspect" in prompt:
        return prompt

    # 将OpenAI的尺寸格式转换为宽高比
    try:
        if 'x' in size:
            width, height = map(int, size.split('x'))
            if width > 0 and height > 0:
                return f"{prompt} --aspect {width}:{height}"
        # 如果不是标准尺寸格式，直接返回原始提示词
        return prompt
    except Exception:
        # 解析失败时返回原始提示词
        return prompt


def format_response(result, prompt=""):
    """
    将Poe的响应格式化为OpenAI格式
    """
    image_url = extract_image_url(result)

    data = {
        "created": int(datetime.now().timestamp()),
        "data": [
            {
                "url": image_url,
                "revised_prompt": prompt
            }
        ]
    }

    return data


def extract_image_url(result):
    """
    从Markdown格式的结果中提取图片URL
    """
    # 假设格式为 ![描述](URL)
    try:
        if '![' in result and '](' in result:
            start_index = result.find('](') + 2
            end_index = result.find(')', start_index)
            if start_index > 1 and end_index > start_index:
                return result[start_index:end_index]

        # 如果上面的解析失败，可能是直接返回了URL
        return result.strip()
    except Exception as e:
        logger.error("提取图片URL失败: %s", e)
        return result  # 返回原始结果
