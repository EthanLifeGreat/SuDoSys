import re

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


def handler(message, cache):
    fName = 'stage2.txt'
    ff = open('./SuDoSys/prompt/' + fName, 'r', encoding='utf-8')
    prompt = ff.read()

    prompt = insert_after_match(prompt, ".*?第一步传递的数据如下：", str(cache['problems']))

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

    data1 = {"problemSelected": ""}
    data1['problemSelected'] = responseJson['problemSelected']
    cache.update(data1)

    return responseJson, cache
