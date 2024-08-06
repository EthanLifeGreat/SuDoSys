import os
from utils.get_portrait import get_portrait
import multiprocessing
from chat_with_models import chat


max_turns = 20
num_portraits = 148


def update_messages(chat_history, max_sentences=5):
    client_model_messages = []
    counselor_model_messages = []

    for i, message in enumerate(chat_history):
        if i % 2 == 0:
            client_model_messages.append({"role": "assistant", "content": message})
            counselor_model_messages.append({"role": "user", "content": message})
        else:
            client_model_messages.append({"role": "user", "content": message})
            counselor_model_messages.append({"role": "assistant", "content": message})

    if len(client_model_messages) > max_sentences:
        client_model_messages = client_model_messages[-max_sentences:]
    return client_model_messages, counselor_model_messages


def data_generator(counselor_model_name):
    try:
        # 不同的baseline模型名，保存的文件路径不一样
        history_file_directory = "./data/history_" + counselor_model_name
        if not os.path.exists(history_file_directory):
            os.makedirs(history_file_directory)

        # portrait_id 是指用户画像的id
        portrait_id = 1
        while portrait_id <= num_portraits:
            '''
                这里历史对话最终会有两种格式，分别是元组和字典数组，元组是因为chatglm4是按照元组解析的（但其实也可以改为字典），
                字典数组是因为create接口统一用这种格式。我们选择的做法是，将所有的对话都转换为字典数组，这样就可以统一处理了。
                但有一个难点，就是assistant字段，调用不同的模型时，assistant字段的含义是不一样的。
            '''
            if counselor_model_name == "SoDuSys":
                chat_history = ["你好，咨询师"]
            else:
                chat_history = ["你好，咨询师", "你好，我是一名咨询师，有什么能帮到你呢？"]
            client_model_messages, counselor_model_messages = update_messages(chat_history)

            cache = None
            # turn 是指对话次数
            turn = 1
            if counselor_model_name == "SoDuSys":
                counselor_model_response, cache = chat(counselor_model_name, [counselor_model_messages[0]], None)
                chat_history.append(counselor_model_response)
                client_model_messages, counselor_model_messages = update_messages(chat_history)
            while turn < max_turns:
                # 生成用户回复，然后更新对话历史，然后用新的对话历史生成咨询师回复
                client_model_response = chat("GLM4-9B-Client", client_model_messages, get_portrait(portrait_id))
                chat_history.append(client_model_response)
                client_model_messages, counselor_model_messages = update_messages(chat_history)
                # 生成咨询师回复，并更新对话历史
                counselor_model_response, cache = chat(counselor_model_name, counselor_model_messages, cache)
                chat_history.append(counselor_model_response)
                client_model_messages, counselor_model_messages = update_messages(chat_history)

                turn += 1
                print(f"Charactor ID: {portrait_id}; Turn: {turn}")

            history_file_name = os.path.join(history_file_directory, f"{counselor_model_name}{portrait_id}.txt")
            portrait_id += 1

            with open(history_file_name, 'w', encoding='utf-8') as file:
                for i, message in enumerate(chat_history):
                    if i % 2 == 0:
                        file.write("\n咨询者：" + message + "\n")
                    else:
                        file.write("咨询师：" + message + "\n")
    except Exception as e:
        print(e)


def main():
    baseline_model_list = ["Qwen2-7B-Counselor", "PsyChat", "CPsyCounX", "SoDuSys"]

    # 串行处理
    # for baseline_model in baseline_model_list:
    #     data_generator(baseline_model)

    # 创建进程池并行处理
    with multiprocessing.Pool(processes=len(baseline_model_list)) as pool:
        # 使用进程池并行运行 data_generator
        pool.map(data_generator, baseline_model_list)


if __name__ == '__main__':
    main()
