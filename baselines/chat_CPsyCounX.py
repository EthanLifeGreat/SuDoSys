import requests
import json
openai_api_base = "http://10.10.1.213:8010/v1"

def chat_with_CPsyCounX(message):
    assert len(message) % 2 != 0, "message length should be an odd number"
    query, history_dict = message[-1]["content"], message[:-1]
    history = []
    for idx, dict_item in enumerate(history_dict):
        if idx % 2 == 0:
            assert dict_item["role"] == "user", "Utterance at odd position should be user's"
        else:
            assert dict_item["role"] == "assistant", "Utterance at odd position should be assistant's"
        history.append(dict_item["content"])

    chat_response = get_cpsycount_response(query, history)
    print(chat_response)
    return chat_response


def get_cpsycount_response(query, history):
    raw_json_data = {
        "query": query,
        "history": history,
    }
    json_data = json.dumps(raw_json_data)
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "PostmanRuntime/7.29.2",
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive"
    }
    response = requests.post(f'{openai_api_base}/completions',
                             data=json_data,
                             headers=headers, verify=False)
    if response.status_code == 200:
        response = json.loads(response.text)
        response_data = response["response"]
    else:
        print(response)
        return "Error"
    return response_data
