import os
import re
from tqdm import tqdm
from openai import OpenAI
import json

input_file = "../data/dh_cpc.json"
output_file = "../data/client_portraits_cpc.json"

max_retry_num = 3

openai_api_key = "EMPTY"
openai_api_base = "http://10.10.1.211:8008/v1"

client = OpenAI(
    api_key=openai_api_key,
    base_url=openai_api_base,
)

system_prompt = "你是一名优秀的文字处理者，你能够从复杂的文字中提取关键信息。"
instruction_start = """现在有一份文本，它是患抑郁症的用户与心理咨询师的对话记录。
请您根据自己的理解，从对话内容中提取用户画像，并且用json格式返回。如果某些内容无法推断，请在相应位置置空。
用户画像有如下指标：

    1.当前情绪（详细描述：如悲伤、焦虑、愤怒等）
    2.当前症状表现（详细描述：如睡眠问题、食欲变化、疲劳感、情绪低落的程度、持续时间、有无自杀念头等）
    3.困扰和压力来源（详细描述：重大生活事件、工作压力等）
    4.推测年龄
    5.推测性别
    6.既往心理健康史
    7.生活习惯（饮食、锻炼、睡眠等）
    8.职业
    9.个人爱好和兴趣

 你的回答仅包含以下json格式的数据为：
    {
        "当前情绪":  "",
        "当前症状表现":  "",
	    "困扰和压力来源": "",
	    "推测年龄": "",
	    "推测性别": "",
	    "既往心理健康史": "",
	    "生活习惯":  "",
	    "职业": "",
	    "个人爱好和兴趣": ""
    }
    以下是对话记录：'''
"""
instruction_end = "'''"


def find_json_blocks(text):
    # 使用正则表达式匹配被```包围的内容
    # 注意：这个正则表达式假设```是单独成行的，即不考虑行内代码块的情况
    # 如果需要匹配行内代码块，正则表达式将需要更复杂的处理
    text = text.replace("json", "").strip()
    pattern = r'(?m)^```([\s\S]*?)```$'
    matches = re.findall(pattern, text, re.MULTILINE)
    if not matches:
        return text
    else:
        return matches[0]


def prompt_once(dialogue_history):
    chat_response = client.chat.completions.create(
        model="Qwen2-72B-Instruct-GPTQ-Int4",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": instruction_start + dialogue_history + instruction_end},
        ]
    )
    return chat_response.choices[0].message.content


def parse_once(r):
    # print(f"Response received: \n{r}")
    parsed_response = json.loads(find_json_blocks(r))
    return parsed_response


if __name__ == "__main__":
    with open(input_file, 'r', encoding='utf-8') as file:
        dialogue_history_jsons = json.load(file)
    # 判断当前文件夹下是否存在client_portraits_cpc.json文件，如果存在则读取该文件，如果不存在则创建一个空列表
    # if os.path.exists('client_portraits_cpc.json'):
    #     with open('client_portraits_cpc.json', 'r', encoding='utf-8') as file:
    #         client_portraits = json.load(file)
    # else:
    #     client_portraits = []
    client_portraits = []
    # 使用tqdm库循环取出dialogue_history_jsons中的每一项，然后调用extract_once函数
    for dialogue_history_json in tqdm(dialogue_history_jsons, desc="Processing"):
        # 取出每一项中的id和history
        cp_id = dialogue_history_json['id']
        history = dialogue_history_json['history']

        try:  # 调用prompt_once函数，获取LLM response
            response = prompt_once(history)
        except Exception as e:
            print(f"Chat with Qwen-2 error: {e}")
            continue
        try:  # 调用parse_once函数，解析response
            parsed_data = parse_once(response)
        except Exception as e:
            print(f"Unhandled parse error:{e}")
            print(f"Response received: \n{response}")
            continue

        client_portrait = {"id": cp_id}
        client_portrait.update(parsed_data)
        client_portraits.append(client_portrait)

        # 将更新后的数据写入output_file文件
        with open(output_file, 'w', encoding='utf-8') as file:
            json.dump(client_portraits, file, ensure_ascii=False, indent=4)

        # print(f"处理完成，数据已写入{output_file}文件。")
