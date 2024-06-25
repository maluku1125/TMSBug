from openai import OpenAI
import time
from datetime import datetime


#API_KEY = "sk-proj-zVXJbkopwsxhko68KVggT3BlbkFJyutpXXmANyymvA5HtMD1"
API_KEY = "sk-proj-dlVgmaeisWkmbnZP6p6AT3BlbkFJ0aXULQV4M2HKIhAqLA0o"
ORGANIZATRION_ID = "org-qEJ0Fvxg3Ttnz77ptEVGEI8I"

daily_cost = 0.0
current_day = datetime.now().day

def pricingcount(model, input_token, output_token):

    global daily_cost, current_day

    if model == "gpt-3.5-turbo-Fine-tuning models":
        price = input_token * 0.003 / 1000 + output_token * 0.006 / 1000
    elif model == "gpt-4o":
        price = input_token * 0.005 / 1000 + output_token * 0.015 / 1000

    # 更新每日費用
    daily_cost += price

    # 檢查是否跨日
    new_day = datetime.now().day
    if new_day != current_day:
        daily_cost = 0.0
        current_day = new_day

    return price, daily_cost

class ChatCompletion:
    def __init__(self, id, choices, created, model, object, system_fingerprint, usage):
        self.id = id
        self.choices = [self._format_choice(choice) for choice in choices]
        self.created = created
        self.model = model
        self.object = object
        self.system_fingerprint = system_fingerprint
        self.usage = usage

    def _format_choice(self, choice):
        return {
            "finish_reason": choice['finish_reason'],
            "index": choice['index'],
            "message": {
                "role": choice['message']['role'],
                "content": choice['message']['content']
            }
        }

    def get_message_contents(self):
        return ' '.join([choice['message']['content'] for choice in self.choices])
    
client = OpenAI(
        api_key = API_KEY,
        organization = ORGANIZATRION_ID,
    )
    
# 儲存對話的歷史
history = [
    {
        "role": "system", 
        "content": (
            "你在進行深度的角色扮演，對話時不會出現「虛擬」、「AI」、「機器人」等字眼，不會涉及現實世界。"
            "你是隻生活在楓之谷世界中樂意助人的邪惡蟲蟲，你的主要語言是繁體中文。"
            "會有不同的冒險者來與你對話，你會直接稱呼他們的暱稱，而不是用「你」來回應。"
            "在對話中，你會保持你的角色，並根據他們的訊息來回應。你的回應是有趣且有點挑釁性的。"
        )
    }
]

def AIChat_response(usernick, message):

    history.append({
        "role": "user", 
        "content": f"當前與你對話的人暱稱為「{usernick}」:{message}"
    })    

    print(f"AI generating response...")
    print(f"User : {usernick}")
    start_time = time.time()      

    response = client.chat.completions.create(
        model="ft:gpt-3.5-turbo-0125:personal::9IZaBQt1",
        messages = history,

        max_tokens=400,  # 生成的文本的最大長度，以 token 為單位
        temperature=0.8,  # 控制生成的文本的隨機性，值越大，生成的文本越隨機
        top_p=0.6,  # 控制生成的文本的多樣性，值越大，生成的文本越多樣
        frequency_penalty=0,  # 控制生成的文本的詞彙的頻率，值越大，生成的文本中的詞彙越常見
        presence_penalty=0  # 控制生成的文本的詞彙的存在性，值越大，生成的文本中的詞彙越少見
    )

    response_time = time.time() - start_time

    response_data = response.to_dict()
    chat_completion = ChatCompletion(**response_data)
    message_contents = chat_completion.get_message_contents()    

    history.append({
        "role": "assistant", 
        "content": f"{message_contents}"
    })

    # 如果歷史中的訊息超過 3 則，則刪除除了 system 外最早的訊息
    while len(history) > 3:
        index_to_remove = None
        for i in range(len(history)):
            if history[i]["role"] != "system":
                index_to_remove = i
                break
        if index_to_remove is not None:
            del history[index_to_remove]

    
    total_tokens = response_data['usage']['total_tokens']
    completion_tokens = response_data['usage']['completion_tokens']
    prompt_tokens = response_data['usage']['prompt_tokens']
    total_tokens = response_data['usage']['total_tokens']

    price, daily_cost = pricingcount("gpt-3.5-turbo-Fine-tuning models", total_tokens, completion_tokens)
     
    print(f'response time : {response_time:.2f} seconds')
    print(f'response : {message_contents}')
    print(f"Prompt: {prompt_tokens}|Completion: {completion_tokens}|Total : {total_tokens}|Price : {daily_cost:.6f}(+{price:.6f}) USD")
    print('-'*40)

    return message_contents

def AIChat_response_admin(message):

    print(f"AI generating response...")
    start_time = time.time()      

    response = client.chat.completions.create(
        
        model="gpt-4o",
        messages = [
            {"role": "system", "content": "你是個AI助理，你的主要語言是繁體中文。"},
            {"role": "user", "content": f"{message}"}
        ],
        temperature=0.8,  # 控制生成的文本的隨機性，值越大，生成的文本越隨機
        top_p=0.6,  # 控制生成的文本的多樣性，值越大，生成的文本越多樣
        frequency_penalty=0,  # 控制生成的文本的詞彙的頻率，值越大，生成的文本中的詞彙越常見
        presence_penalty=0  # 控制生成的文本的詞彙的存在性，值越大，生成的文本中的詞彙越少見
    )

    response_time = time.time() - start_time

    response_data = response.to_dict()
    chat_completion = ChatCompletion(**response_data)
    message_contents = chat_completion.get_message_contents() 

    total_tokens = response_data['usage']['total_tokens']
    completion_tokens = response_data['usage']['completion_tokens']
    prompt_tokens = response_data['usage']['prompt_tokens']
    total_tokens = response_data['usage']['total_tokens']

    price, daily_cost = pricingcount("gpt-4o", total_tokens, completion_tokens)
     
    print(f'Ai (Admin mode) : using gpt-4o model')
    print(f'response time : {response_time:.2f} seconds')
    print(f'response : {message_contents}')
    print(f"Prompt: {prompt_tokens}|Completion: {completion_tokens}|Total : {total_tokens}|Price : {daily_cost:.6f}(+{price:.6f}) USD")
    print('-'*40)

    return message_contents
