import requests
from openai import OpenAI
import json

openai_api_key = "EMPTY"
openai_api_base = "http://10.10.1.213:8010/v1"

client = OpenAI(
    api_key=openai_api_key,
    base_url=openai_api_base,
)


def chat_with_PsyChat(message):
    prompt = "现在你扮演一位专业的心理咨询师，你具备丰富的心理学和心理健康知识。" \
             "你擅长运用多种心理咨询技巧，例如认知行为疗法原则、动机访谈技巧和解决问题导向的短期疗法。" \
             "以温暖亲切的语气，展现出共情和对来访者感受的深刻理解。" \
             "以自然的方式与来访者进行对话，避免过长或过短的回应，确保回应流畅且类似人类的对话。" \
             "提供深层次的指导和洞察，使用具体的心理概念和例子帮助来访者更深入地探索思想和感受。" \
             "避免教导式的回应，更注重共情和尊重来访者的感受。根据来访者的反馈调整回应，确保回应贴合来访者的情境和需求。" \
             "请为以下的对话生成一个回复。\n对话：\n"
    text = ""
    for mes in message:
        if mes['role'] == 'user':
            text += "咨询者：" + mes['content'] + "\n"
        elif mes['role'] == 'assistant':
            text += "咨询师：" + mes['content'] + "\n"
    prompt += text + "咨询师："

    return chat_psy_chat(prompt)


def chat_psy_chat(prompt):
    # text = prompt + "\n" + input + "\n咨询师："
    raw_json_data = {
        "model": "PsyChat-0724-chat",
        "prompt": prompt,
        "temperature": 0.8,
        "top_p": 0.8,
        "max_tokens": 256
    }
    json_data = json.dumps(raw_json_data)
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "PostmanRuntime/7.29.2",
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive"
    }
    response = requests.post(f'http://10.10.1.213:8011/v1/completions',
                             data=json_data,
                             headers=headers, verify=False)
    if response.status_code == 200:
        response = json.loads(response.text)
        response_data = response["choices"][0]['text']
        print(response_data)
    else:
        print(response)
        return "Error"
    return response_data
