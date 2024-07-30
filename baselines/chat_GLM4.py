from openai import OpenAI
import json

openai_api_key = "EMPTY"
openai_api_base = "http://10.10.1.213:8009/v1"

client = OpenAI(
    api_key=openai_api_key,
    base_url=openai_api_base,
)


def chatUserInput(prompt, lastOutput):
    chat_response = open_ai_chat(
        model="GLM-4-9B-chat",
        messages=[
            {"role": "system", "content": "你是一位沉默寡言的咨询者，你只会回答关键信息。"},
            {"role": "user", "content": prompt + "\n咨询者："},
            # {"role": "user", "content": lastOutput},
        ],
        streaming=True
    )
    print("prompt:" + prompt + "\n咨询者：")
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
            temperature=0.95,
            max_tokens=1024,
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
            temperature=0.95,
            max_tokens=1024,
        )
        print("user:")
        for chunk in messages:
            chunk_message = chunk.choices[0].delta.content  # extract the message
            if not chunk_message:  # if the message is empty, skip it
                continue
            chat_response += chunk_message  # save the message
            print(chunk_message, end="", flush=True)  # print the response stream
    return chat_response
