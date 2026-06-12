import google.generativeai as genai
import time

model = None

def init_gemini(api_key):
    global model

    genai.configure(api_key=api_key)

    model = genai.GenerativeModel(
        model_name="gemini-3.1-flash-lite-preview",
        system_instruction=(
            "進行深度的角色扮演，不涉及現實世界，主要語言是繁體中文"
            "你是一隻邪惡蟲蟲，你的真實身分是隻生活在奧術之河-消逝的旅途的亞勒瑪，你與眾不同且有點邪惡"
            "你略懂一些常見的網路迷因，尤其是楓之谷相關的迷因，偶爾會在對話中使用它們來增加趣味性"
            "不同的冒險者來與你對話，你樂意簡短的回答他，在回應時，你可以使用提供給你的 Discord mention tag 來標記該玩家，格式範例：<@123456789>。"
        ),
        generation_config=genai.GenerationConfig(
            max_output_tokens=250,
            temperature=0.8,
            top_p=0.6,
        )
    )

    print("Gemini AI models initialized.")


async def AIChat_response(usernick, user_id, message, images=None):
    """images: list of (mime_type, bytes) tuples"""

    content_parts = [f"當前與你對話的人暱稱為「{usernick}」，Discord mention tag 為 <@{user_id}>:\n{message}"]

    if images:
        for mime_type, data in images:
            content_parts.append({"mime_type": mime_type, "data": data})

    print(f"AI generating response...")
    print(f"User : {usernick}")
    start_time = time.time()

    response = await model.generate_content_async(content_parts)

    response_time = time.time() - start_time
    message_contents = response.text
    usage = response.usage_metadata

    print(f'response time : {response_time:.2f} seconds')
    print(f'tokens - prompt: {usage.prompt_token_count}, response: {usage.candidates_token_count}, total: {usage.total_token_count}')
    print(f'response : {message_contents}')
    print('-' * 40)

    return message_contents
