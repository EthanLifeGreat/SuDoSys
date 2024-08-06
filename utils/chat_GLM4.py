from openai import OpenAI

client_prompt = "你是一位沉默寡言的并且身处困境的人，你正向另一位心理咨询师咨询你遇到的问题并和他探讨解决方案。" \
                "你要根据咨询师的发言直接给出作为咨询者的50字以内的发言内容，你要使用第一人称、使用中文回复，不要重复你已经说过的内容。" \
                "你要扮演的咨询者基本信息如下：\n"

openai_api_key = "EMPTY"
openai_api_base = "http://10.10.1.213:8009/v1"

client = OpenAI(
    api_key=openai_api_key,
    base_url=openai_api_base,
)


def chat_with_GLM4_client(messages, portrait):
    system_message = {"role": "system", "content": client_prompt + portrait}
    messages.append(system_message)
    return chat_GLM4(messages)


def chat_GLM4(messages):
    chat_response = open_ai_chat(
        model="GLM-4-9B-chat",
        messages=messages,
        streaming=True
    )
    return chat_response


def open_ai_chat(model, messages, streaming=False):
    if not streaming:
        chat_response = client.chat.completions.create(
            model=model,
            messages=messages,
            # 设置额外参数
            extra_body={
                "stop_token_ids": [151329, 151336, 151338]
            },
            temperature=0.8,
            max_tokens=256,
        )
    else:
        chat_response = ''
        messages = client.chat.completions.create(
            model=model,
            messages=messages,
            stream=True,
            # 设置额外参数
            extra_body={
                "stop_token_ids": [151329, 151336, 151338]
            },
            temperature=0.8,
            max_tokens=256,
        )
        print("user:")
        for chunk in messages:
            chunk_message = chunk.choices[0].delta.content  # extract the message
            if not chunk_message:  # if the message is empty, skip it
                continue
            chat_response += chunk_message  # save the message
            print(chunk_message, end="", flush=True)  # print the response stream
    return chat_response
