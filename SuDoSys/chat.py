import importlib
import re
from typing import Iterable, Any, Union, Dict
from openai import OpenAI
import json

from openai.types.chat import ChatCompletionMessageParam

openai_api_key = "EMPTY"
openai_api_base = "http://10.10.1.213:8008/v1"

client = OpenAI(
    api_key=openai_api_key,
    base_url=openai_api_base,
)

max_try_times = 10
max_stages = 6
max_stage = 6
max_turns_per_stage = 3


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
            print(f"大模型回复格式有误，重试了第{tried_times}次，错误回复：\n" + ori_chat_response)

    if not success_flag:
        print("无法生成能够被解析的json")

    return responseJson


def chat_with_SuDoSys(message: Iterable[ChatCompletionMessageParam], _cache: Union[Dict, None] = None) -> Any:
    print(f"Handling SuDoSys")
    if not _cache:
        _cache = {'stage': 1}
    if _cache['stage'] > max_stage:
        _cache['stage'] = max_stage
    elif _cache['stage'] <= 0:
        _cache['stage'] = 1
    stage = _cache['stage']

    if "current_stage_turns" not in _cache:
        _cache["current_stage_turns"] = 0
    # 这里可以添加更多的逻辑，包括使用cache
    '''
        不同stage不同的prompt处理逻辑
    '''
    module_name = f'SuDoSys.stage.stage{stage}'
    # 使用importlib动态导入模块
    module = importlib.import_module(module_name)
    print("[stage" + str(stage) + "]")

    response_json, _cache = module.handler(message, _cache)
    _cache["current_stage_turns"] += 1

    if response_json["finished"] == '1' or _cache["current_stage_turns"] >= max_turns_per_stage:
        _cache['stage'] += 1
        _cache["current_stage_turns"] = 0

    return response_json['response'], _cache


if __name__ == '__main__':
    cache = None
    messages = []
    while True:
        user_input = input("咨询者：")
        messages.append({"role": "user", "content": user_input})
        response, cache = chat_with_SuDoSys(messages, cache)
        messages.append({"role": "assistant", "content": response})
