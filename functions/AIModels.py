"""
AIModels.py
===========
Gemini 對話模型封裝。

2026-08 遷移自已停止支援的 google-generativeai 套件 → google-genai。
模型名稱與參數改由 config.ini [config] 提供，模型下架時只需改設定。
"""

import time
import asyncio
from google import genai
from google.genai import types

client = None
MODEL_NAME = None

# 預設值（config 未指定時使用）
DEFAULT_MODEL = "gemini-3.5-flash-lite"
DEFAULT_TIMEOUT = 30        # 單次生成逾時（秒）
DEFAULT_MAX_TOKENS = 250
DEFAULT_TEMPERATURE = 0.8
DEFAULT_TOP_P = 0.6
# 思考模式：留空 = 不送此參數（多數 flash-lite 本來就不思考，硬送 budget=0 會 400）
# 可填 minimal/low/medium/high（thinking_level）或正整數（thinking_budget）
DEFAULT_THINKING = ""
DEFAULT_SAFETY = "relaxed"      # default / relaxed / off
DEFAULT_MEDIA_RES = "low"       # low / medium / high / default

# 安全過濾預設組合。角色設定本身帶點嗆人，過嚴會被擋下導致無回應。
_SAFETY_PRESETS = {
    "default": None,                              # 用 API 預設
    "relaxed": types.HarmBlockThreshold.BLOCK_ONLY_HIGH,
    "off": types.HarmBlockThreshold.BLOCK_NONE,
}
_SAFETY_CATEGORIES = [
    types.HarmCategory.HARM_CATEGORY_HARASSMENT,
    types.HarmCategory.HARM_CATEGORY_HATE_SPEECH,
    types.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
    types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
]
_MEDIA_RES = {
    "low": types.MediaResolution.MEDIA_RESOLUTION_LOW,
    "medium": types.MediaResolution.MEDIA_RESOLUTION_MEDIUM,
    "high": types.MediaResolution.MEDIA_RESOLUTION_HIGH,
    "default": None,
}


def _build_thinking(value):
    """把設定值轉成 ThinkingConfig；留空或無法解析則回 None（不送參數）。

    注意：部分模型（如 gemini-3.5-flash-lite）不支援 thinking_budget=0，
    會回 400；這類模型本來就不產生思考 token，直接不送即可。
    """
    if value is None:
        return None
    v = str(value).strip().lower()
    if v in ("", "default", "none", "off"):
        return None
    levels = {
        "minimal": types.ThinkingLevel.MINIMAL,
        "low": types.ThinkingLevel.LOW,
        "medium": types.ThinkingLevel.MEDIUM,
        "high": types.ThinkingLevel.HIGH,
    }
    if v in levels:
        return types.ThinkingConfig(thinking_level=levels[v])
    try:
        n = int(v)
    except ValueError:
        print(f"Gemini AI: 無法解析 thinking 設定 {value!r}，已忽略")
        return None
    if n <= 0:
        print("Gemini AI: thinking_budget<=0 部分模型不支援，改為不送此參數")
        return None
    return types.ThinkingConfig(thinking_budget=n)


def _build_safety(preset):
    th = _SAFETY_PRESETS.get((preset or "default").lower())
    if th is None:
        return None
    return [types.SafetySetting(category=c, threshold=th) for c in _SAFETY_CATEGORIES]

SYSTEM_INSTRUCTION = (
    "進行深度的角色扮演，不涉及現實世界，主要語言是繁體中文"
    "你是一隻邪惡蟲蟲，你的真實身分是隻生活在奧術之河-消逝的旅途的亞勒瑪，你與眾不同且有點邪惡"
    "你略懂一些常見的網路迷因，尤其是楓之谷相關的迷因，偶爾會在對話中使用它們來增加趣味性"
    "不同的冒險者來與你對話，你樂意簡短的回答他，在回應時，你可以使用提供給你的 Discord mention tag "
    "來標記該玩家，格式範例：<@123456789>。"
)

_generation_config = None
_timeout = DEFAULT_TIMEOUT


class AIUnavailable(Exception):
    """AI 無法回應（未初始化、逾時、被安全機制擋下等），呼叫端應改回覆固定台詞"""


def init_gemini(api_key, model_name=None, max_tokens=DEFAULT_MAX_TOKENS,
                temperature=DEFAULT_TEMPERATURE, top_p=DEFAULT_TOP_P,
                timeout=DEFAULT_TIMEOUT, thinking=DEFAULT_THINKING,
                safety=DEFAULT_SAFETY, media_resolution=DEFAULT_MEDIA_RES):
    global client, MODEL_NAME, _generation_config, _timeout

    if not api_key:
        print("Gemini AI: 未設定 API key，AI 功能停用")
        return False

    try:
        client = genai.Client(api_key=api_key)
        MODEL_NAME = model_name or DEFAULT_MODEL
        _timeout = timeout
        kwargs = dict(
            system_instruction=SYSTEM_INSTRUCTION,
            max_output_tokens=max_tokens,
            temperature=temperature,
            top_p=top_p,
        )
        tc = _build_thinking(thinking)
        if tc is not None:
            kwargs["thinking_config"] = tc
        safety_settings = _build_safety(safety)
        if safety_settings:
            kwargs["safety_settings"] = safety_settings
        mr = _MEDIA_RES.get((media_resolution or "default").lower())
        if mr is not None:
            kwargs["media_resolution"] = mr

        _generation_config = types.GenerateContentConfig(**kwargs)
        print(f"Gemini AI models initialized. (model={MODEL_NAME}, "
              f"thinking={thinking or 'default'}, safety={safety}, media={media_resolution})")
        return True
    except Exception as e:
        client = None
        print(f"Gemini AI 初始化失敗: {type(e).__name__}: {e}")
        return False


def _extract_text(response) -> str:
    """安全取出回應文字。

    被安全機制擋下或無候選時，response.text 會拋例外或為空，
    此處統一轉成 AIUnavailable 讓呼叫端回覆固定台詞。
    """
    try:
        text = response.text
    except Exception:
        text = None
    if not text or not text.strip():
        reason = None
        try:
            if response.candidates:
                reason = response.candidates[0].finish_reason
        except Exception:
            pass
        raise AIUnavailable(f"empty response (finish_reason={reason})")
    return text.strip()


async def AIChat_response(usernick, user_id, message, images=None):
    """images: list of (mime_type, bytes) tuples。失敗時拋 AIUnavailable。"""
    if client is None:
        raise AIUnavailable("client not initialized")

    parts = [types.Part.from_text(
        text=f"當前與你對話的人暱稱為「{usernick}」，Discord mention tag 為 <@{user_id}>:\n{message}")]
    for mime_type, data in (images or []):
        parts.append(types.Part.from_bytes(data=data, mime_type=mime_type))

    print("AI generating response...")
    print(f"User : {usernick}")
    start_time = time.time()

    try:
        response = await asyncio.wait_for(
            client.aio.models.generate_content(
                model=MODEL_NAME,
                contents=[types.Content(role="user", parts=parts)],
                config=_generation_config,
            ),
            timeout=_timeout,
        )
    except asyncio.TimeoutError:
        print(f"AI timeout after {_timeout}s")
        raise AIUnavailable("timeout")

    text = _extract_text(response)

    response_time = time.time() - start_time
    usage = response.usage_metadata
    print(f'response time : {response_time:.2f} seconds')
    if usage:
        print(f'tokens - prompt: {usage.prompt_token_count}, '
              f'response: {usage.candidates_token_count}, total: {usage.total_token_count}')
    print(f'response : {text}')
    print('-' * 40)

    return text
