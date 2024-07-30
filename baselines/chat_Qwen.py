from openai import OpenAI
import json

openai_api_key = "EMPTY"
openai_api_base = "http://10.10.1.211:8008/v1"

client = OpenAI(
    api_key=openai_api_key,
    base_url=openai_api_base,
)


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


def chat_with_Qwen(conversation):
    sys_prompt = [
        {"role": "system", "content": "现在你扮演一位专业的心理咨询师，以温暖亲切的语气，展现出共情和对来访者感受的深刻理解。"
                                      "以自然的方式与用户进行对话，确保回应流畅且类似人类的对话。"
                                      "请注重共情和尊重用户的感受。根据用户的反馈调整回应，确保回应贴合用户的情境和需求。"
                                      "如果在对话过程中产生了你不清楚的细节，你应当追问用户这些细节。"
                                      "当你明确了来访者在生活中遇到问题时，可以帮助他们思考解决对策，但应该避免直接提供建议。"
                                      "记住，你就是一名心理咨询师，请不要让用户寻求除了你以外的其它心理咨询。"
                                      "你的回复应当简洁明了。请将每一次的回复长度严格限定在100字以内。"}
    ]
    conversation = sys_prompt + conversation
    chat_response = open_ai_chat(
        model="Qwen2-7B-Instruct",
        messages=conversation,
        streaming=True
    )
    return chat_response
