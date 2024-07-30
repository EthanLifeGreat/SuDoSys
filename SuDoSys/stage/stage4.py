from openai import OpenAI
import re

openai_api_key = "EMPTY"
openai_api_base = "http://10.10.1.211:8008/v1"

client = OpenAI(
    api_key=openai_api_key,
    base_url=openai_api_base,
)
'''
字符串正则查找位置并拼接
'''
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
def handler(message,cache):
    fName = 'stage4.txt'
    ff = open('./SuDoSys/prompt/' + fName, 'r', encoding='utf-8')
    prompt = ff.read()

    prompt = insert_after_match(prompt, ".*?第三步传递的数据如下：", "问题："+str(cache['problemSelected'])+"，影响因素："+str(cache['factors']))
    newInput = ""
    lastMessage = ""
    conversation = message.copy()
    if conversation:
        if conversation[-1]['role'] == 'user':
            newInput = conversation.pop()['content']

        if conversation and conversation[-1]['role'] == 'assistant':
            lastMessage = conversation.pop()['content']
    from SuDoSys import chat
    responseJson = chat.chatReturnJson(prompt, lastMessage, newInput)
    print(responseJson)


    # 文件路径

    data1 = {"solutions":[]}
    data1["solutions"] = responseJson['solutions']
    cache.update(data1)

    return responseJson,cache