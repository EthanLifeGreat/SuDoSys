import re

from openai import OpenAI
import json

openai_api_key = "EMPTY"
openai_api_base = "http://10.10.1.211:8008/v1"

client = OpenAI(
    api_key=openai_api_key,
    base_url=openai_api_base,
)

max_try_times = 10

def find_json_blocks(text):
    text = text.replace("json", "").strip()
    pattern = r'(?m)^```([\s\S]*?)```$'
    # matches = re.findall(pattern, text, re.MULTILINE)
    matches = iter(re.finditer(pattern, text, re.MULTILINE))
    try:
        # 获取第一个匹配项，并返回其组内的内容（即 JSON 字符串）
        return next(matches).group(1)
    except StopIteration:
        # 如果没有找到匹配项，返回原始文本（或根据需要返回 None）
        return text


def chatReturnJson(prompt, lastMessage, userInput):
    instruction = f"{prompt}\n你对用户说的最后一句话是：{lastMessage}\n对此，用户的回复是：{userInput}"
    tried_times = 0
    responseJson = None
    success_flag = False
    while (not success_flag) and (tried_times <= max_try_times):
        ori_chat_response = open_ai_chat(
            model="Qwen2-7B-Instruct",
            messages=[
                {"role": "user", "content": instruction},
            ],
            streaming=True
        )
        tried_times += 1
        try:
            # responseJson = json.loads(chat_response.choices[0].message.content)
            chat_response = find_json_blocks(ori_chat_response)
            chat_response = chat_response.replace("'", '"')
            responseJson = json.loads(chat_response)
            if responseJson["finished"] == "1" or responseJson["finished"] == "0":
                success_flag = True
                break
        except json.decoder.JSONDecodeError as e:
            print(f"大模型回复格式有误，重试了第{tried_times}次，错误回复：\n"+ori_chat_response)

    if not success_flag:
        print("无法生成能够被解析的json")

    return responseJson


def open_ai_chat(model, messages, streaming=False):
    if not streaming:
        chat_response = client.chat.completions.create(
            model=model,
            messages=messages
        )
    else:
        chat_response = ''
        messages = client.chat.completions.create(
            model=model,
            messages=messages,
            stream=True
        )
        for chunk in messages:
            chunk_message = chunk.choices[0].delta.content  # extract the message
            if not chunk_message:  # if the message is empty, skip it
                continue
            chat_response += chunk_message  # save the message
            print(chunk_message, end="", flush=True)  # print the response stream
    return chat_response
