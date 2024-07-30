import importlib
import json
import re
from typing import Optional, Iterable, Dict, Any, Callable

from openai import OpenAI
from openai.types.chat import ChatCompletionMessageParam
from typing_extensions import Literal

from utils import chatuser
from utils.charactor import genCharactor
from utils.chatCpsycoun import chat_cpsycount_query
from utils.chatPsychat import chat_psy_chat_query
from utils.chatQwen import chatQwenQuery


def insert_after_match(text, pattern, to_insert):
    # 使用正则表达式查找模式
    match = re.search(pattern, text)
    if match:
        # 找到匹配的开始位置
        start_index = match.start()
        # 可以通过match.end()找到匹配的结束位置，但这里我们假设要插入在匹配内容之后
        # 切片文本以获取两部分：匹配前和匹配后
        before_match = text[:start_index + len(match.group())]  # 包括匹配内容
        after_match = text[start_index + len(match.group()):]  # 匹配内容之后的部分
        # 拼接字符串
        result = before_match + to_insert + after_match
        return result
    else:
        # 如果没有找到匹配项，则返回原始文本或进行其他处理
        return text


def create(model: Literal["Qwen2-7B-Instruct", "PsyChat-0724-chat", "CPsyCoun-0724-chat", "SoDuSys"],
           message: Iterable[ChatCompletionMessageParam],
           cache: Optional[dict] = None,
           ):
    ResultFunc = Callable[[Iterable[ChatCompletionMessageParam], Optional[dict]], Any]
    model_handlers: Dict[
        Literal["Qwen2-7B-Instruct", "PsyChat-0724-chat", "CPsyCoun-0724-chat", "SoDuSys"], ResultFunc] = {
        "Qwen2-7B-Instruct": lambda msg, cache: handle_qwen2(msg, cache),
        "PsyChat-0724-chat": lambda msg, cache: handle_psychat(msg, cache),
        "CPsyCoun-0724-chat": lambda msg, cache: handle_cpsycoun(msg, cache),
        "SoDuSys": lambda msg, cache: handle_sudosys(msg, cache),
    }

    def handle_qwen2(_message: Iterable[ChatCompletionMessageParam], _: None) -> Any:
        # 处理Qwen2模型的逻辑
        print(f"Handling Qwen2 model")
        conversation = [
            {"role": "system", "content": "现在你扮演一位专业的心理咨询师，以温暖亲切的语气，展现出共情和对来访者感受的深刻理解。"
                                          "以自然的方式与用户进行对话，确保回应流畅且类似人类的对话。"
                                          "请注重共情和尊重用户的感受。根据用户的反馈调整回应，确保回应贴合用户的情境和需求。"
                                          "如果在对话过程中产生了你不清楚的细节，你应当追问用户这些细节。"
                                          "当你明确了来访者在生活中遇到问题时，可以帮助他们思考解决对策，但应该避免直接提供建议。"
                                          "记住，你就是一名心理咨询师，请不要让用户寻求除了你以外的其它心理咨询。"
                                          "你的回复应当简洁明了。请将每一次的回复长度严格限定在100字以内。"}
        ]
        conversation += _message
        response = chatQwenQuery(conversation)
        return response, None

    def handle_psychat(_message: Iterable[ChatCompletionMessageParam], _: None) -> Any:
        # 处理PsyChat模型的逻辑
        print(f"Handling PsyChat model")
        response = chat_psy_chat_query(_message)
        return response, None

    def handle_cpsycoun(message: Iterable[ChatCompletionMessageParam], _: None) -> Any:
        # 处理CPsyCoun模型的逻辑
        print(f"Handling CPsycount model")
        response = chat_cpsycount_query(message)
        return response, None

    def handle_sudosys(message: Iterable[ChatCompletionMessageParam], _cache: dict) -> Any:
        print(f"Handling Sudosys")
        max_stage = 6
        max_turns_per_stage = 3
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
        module_name = f'stage.stage{stage}'
        # 使用importlib动态导入模块
        module = importlib.import_module(module_name)
        print("[stage" + str(stage) + "]")

        response_json, _cache = module.handler(message, _cache)
        _cache["current_stage_turns"] += 1
        '''
        stage切换条件
        '''
        if response_json["finished"] == '1' or _cache["current_stage_turns"] >= max_turns_per_stage:
            _cache['stage'] += 1
            _cache["current_stage_turns"] = 0

        return response_json['response'], _cache

    handler = model_handlers.get(model)
    if handler is None:
        # 不存在的模型处理
        raise ValueError(f"Unsupported model: {model}")
    return handler(message, cache)


'''
直接测试demo 将下面一段全部解除注释即可 这段是调用我们的模型，从stage1开始，聊天记录上限20句
'''
# flag=1
# message = []
# cache= {"stage":1,"problems":["和丈夫吵架"],"problemSelected" : "和丈夫吵架","factors":["家庭财务分配", "子女教育理念", "个人兴趣与时间安排"],
#     "solutions": ["我们可以制定一个家庭财务预算计划，确保每笔支出都在可控范围内，同时增加透明度，让双方都参与到财务决策中。",
#     "针对子女教育，我们可以进行一次深入的对话，了解各自的教育理念和担忧，尝试找到共同点和妥协方案。",
#     "我们可以一起制定个人兴趣与时间安排的共享日历，确保双方都有足够的个人空间，同时尽量安排共同活动增加亲密感。"
#   ]}
# while flag<=20:
#     userInput = input("用户：")
#     message.append({'role': 'user', 'content': userInput})
#     newRes = create("SoduSys", message, cache)
#     message.append({'role': 'assistant', 'content': newRes[0]})
#     cache = newRes[1]
#     print("当前消息"+str(message))
#     flag+=1
