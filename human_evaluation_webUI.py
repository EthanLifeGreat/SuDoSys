# Copyright (c) Alibaba Cloud.
#
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.

"""A simple web interactive chat demo based on gradio."""
import json

from utils.ssid import generate_ssid
from argparse import ArgumentParser
import gradio as gr
from openai import OpenAI
import random
import pandas as pd
from utils.backend_main import create

model_name_list = ["Qwen2-7B-Instruct", "PsyChat-0724-chat", "CPsyCoun-0724-chat", "SoDuSys"]

# Set OpenAI's API key and API base to use vLLM's API server.
openai_api_key = "EMPTY"
openai_api_base = "http://10.10.1.211:8008/v1"
client = OpenAI(
    api_key=openai_api_key,
    base_url=openai_api_base,
)

# read metric.txt into metrics string
with open("data/metrics.txt", "r", encoding="utf-8") as f:
    metric_str = f.read()

# read metric.txt into metrics string
with open("data/client_portraits_cpc.json", 'r', encoding='utf-8') as file:
    client_portraits_cpc = json.load(file)

# read metric.txt into metrics string
with open("data/client_portrait_intro.txt", "r", encoding="utf-8") as f:
    cp_intro_str = f.read()


df_headers = ["AI咨询师", "逻辑性", "专业性", "同理心", "真实性"]
default_dataframe_value = [
    ["咨询师1", 0, 0, 0, 0],
    ["咨询师2", 0, 0, 0, 0],
    ["咨询师3", 0, 0, 0, 0],
    ["咨询师4", 0, 0, 0, 0],
]
default_dataframe_value = pd.DataFrame(default_dataframe_value, columns=df_headers)


def _get_args():
    parser = ArgumentParser()
    parser.add_argument("--share", action="store_true", default=False,
                        help="Create a publicly shareable link for the interface.")
    parser.add_argument("--inbrowser", action="store_true", default=False,
                        help="Automatically launch the interface in a new tab on the default browser.")
    parser.add_argument("--server-port", type=int, default=8000,
                        help="Demo server port.")
    parser.add_argument("--server-name", type=str, default="0.0.0.0",
                        help="Demo server name.")

    args = parser.parse_args()
    return args


def _gc():
    import gc
    gc.collect()


def _launch_demo(args):
    def predict(_query, _chatbot, _task_history, _model_id, _sds_cache, _scores):
        print(f"User: {_query}")
        _chatbot.append((_query, ""))

        conversation = []
        for query_h, response_h in _task_history:
            conversation.append({'role': 'user', 'content': query_h})
            conversation.append({'role': 'assistant', 'content': response_h})
        conversation.append({'role': 'user', 'content': _query})

        model_name = model_name_list[_scores["model_mapping"][_model_id-1]-1]
        print(model_name)
        if len(_sds_cache) > 1:
            cache = _sds_cache[-1]
        else:
            cache = None
        response, tmp = create(model_name, conversation, cache)
        _sds_cache.append(tmp)
        _chatbot[-1] = (_query, response)
        yield _chatbot

        # print(f"History: {_task_history}")
        _task_history.append((_query, response))
        # print(f"Qwen2-Instruct: {response}")

    def reset_user_input():
        return gr.update(value="")

    def reset_state(_chatbot, _task_history, _sds_cache):
        _task_history.clear()
        _chatbot.clear()
        _gc()
        _sds_cache = {"stage": 1}
        return _chatbot

    def update_dataframe(_scores):
        # 这里假设 scores 中包含了模型的分数
        data = [
            ["咨询师1", _scores["model_1"][0], _scores["model_1"][1], _scores["model_1"][2], _scores["model_1"][3]],
            ["咨询师2", _scores["model_2"][0], _scores["model_2"][1], _scores["model_2"][2], _scores["model_2"][3]],
            ["咨询师3", _scores["model_3"][0], _scores["model_3"][1], _scores["model_3"][2], _scores["model_3"][3]],
            ["咨询师4", _scores["model_4"][0], _scores["model_4"][1], _scores["model_4"][2], _scores["model_4"][3]],
        ]
        _df = pd.DataFrame(data, columns=["AI咨询师", "逻辑性", "专业性", "同理心", "真实性"])
        return _df

    js_func = """
    function refresh() {
        const url = new URL(window.location);
        if (url.searchParams.get('__theme') !== 'dark') {
            url.searchParams.set('__theme', 'dark');
            window.location.href = url.href;
        }
    }
    """

    def process_form(selection1, selection2, selection3, selection4, state, _model_id):
        if selection1 and selection2 and selection3 and selection4:
            # 生成结果
            out = f"咨询师{_model_id}分数保存成功！\n逻辑性: {selection1}\n专业性: {selection2}" \
                  f"\n同理心: {selection3}\n真实性: {selection4}\n\n# 所有评分保存完成后请在页面最下面表格处点击刷新后提交！"
            result = [selection1, selection2, selection3, selection4]
            # 更新状态
            state[f"model_{_model_id}"] = result
            # state[str(time.time())] = result
            # print(state)
            return out
        else:
            return "存在缺省值，请检查是否所有方面已填写。"

    def get_random_cp():
        num_client_portraits = len(client_portraits_cpc)
        _id = random.randint(0, num_client_portraits-1)

        return json.dumps(client_portraits_cpc[_id], indent=4, separators=(',', ': '), ensure_ascii=False)

    def generate_random_array():
        random_list = random.sample(range(1, 5), 4)  # 生成1到4的随机排列
        for _i in random_list:
            print(model_name_list[_i - 1])
        # print(random_list)
        return random_list

    # 示例提交按钮的处理函数（可以根据需要添加具体实现）
    def on_whole_submit(_scores, _df):
        pd_df = pd.DataFrame(_df)
        # 检查是否存在 0 值
        contains_zero = (pd_df == 0).any().any()

        # 检查是否存在 None 值
        contains_none = pd_df.isnull().any().any()
        if contains_zero or contains_none:
            return "存在缺省值，请检查是否所有模型结果已提交。"
        print(_scores, _df)
        for _model_id in range(1, 5):
            model_name = model_name_list[_scores["model_mapping"][_model_id-1]-1]
            # pd_df中名为"AI咨询师"的列中的行号为_model_id行的值修改为model_name
            pd_df.loc[_model_id-1, "AI咨询师"] = model_name
        # 保存到本地文件
        ssid = generate_ssid()
        pd_df.to_csv(f"./results/result_{ssid}.csv", index=False)

        return "全部评价结果已提交！感谢您参与本次测评！🌹🌹🌹"

    with gr.Blocks(title='心理咨询聊天机器人测评', js=js_func) as demo:

        gr.Markdown(
            """<p align="center"><img src="https://www.siat.ac.cn/images/logo2016.png?v1.0" 
            style="height: 60px"/><p>""")
        gr.Markdown("""<center><font size=8>心理咨询聊天机器人测评</center>""")
        gr.Markdown(
            """\
<left><font size=3>欢迎您来到我们的心理咨询聊天机器人测评页面。\
在这个页面中，您将评估4名AI心理咨询师对同一位客户的提供的心理咨询对话内容，并为每个AI咨询师的以下四个方面进行评分（从1、2、3、4、5分中选择一个，5分表示最好，1分表示最差）。以下是参考评价标准和人设。
</left>""")
        model_mapping = gr.State(generate_random_array())

        scores = gr.State({"model_1": [0, 0, 0, 0], "model_2": [0, 0, 0, 0], "model_3": [0, 0, 0, 0], "model_4": [0, 0, 0, 0],
                           "model_mapping": model_mapping.value})

        with gr.Row():
            gr.Textbox(value=metric_str, interactive=False, label="参考评价标准")
            with gr.Column():
                gr.Textbox(value=cp_intro_str, interactive=False, label="参考咨询者画像")
                client_portraits_tb = gr.Textbox(value="", interactive=False, label="画像")
                cp_renew_button = gr.Button("👀查看下一个画像")

        cp_renew_button.click(fn=get_random_cp, outputs=client_portraits_tb)
        sds_cache = gr.State([])


        for r in range(1, 3):
            with gr.Row():
                for c in range(1, 3):
                    with gr.Column():
                        i = (r - 1) * 2 + c
                        gr.Markdown(f"\n# 以下是您与AI咨询师{i}的对话框：")
                        chatbot = gr.Chatbot(label=f'AI咨询师{i}', elem_classes="control-height", show_copy_button=True)
                        query = gr.Textbox(lines=2, label='Input')
                        task_history = gr.State([])

                        model_id = gr.State(i)

                        with gr.Row():
                            empty_btn = gr.Button("🧹 Clear History (清除历史)")
                            submit_btn = gr.Button("🚀 Submit (发送)")

                        submit_btn.click(predict, [query, chatbot, task_history, model_id, sds_cache, scores],
                                         [chatbot], show_progress="full")
                        submit_btn.click(reset_user_input, [], [query])
                        empty_btn.click(reset_state, [chatbot, task_history, sds_cache], outputs=[chatbot],
                                        show_progress="full")

                        gr.Markdown(f"## 请对AI咨询师{i}的以下4个方面进行评分：")
                        with gr.Row():
                            logic_score = gr.Radio(["1", "2", "3", "4", "5"], label="逻辑性")
                            prof_score = gr.Radio(["1", "2", "3", "4", "5"], label="专业性")

                        with gr.Row():
                            empathy_score = gr.Radio(["1", "2", "3", "4", "5"], label="同理心")
                            authentic_score = gr.Radio(["1", "2", "3", "4", "5"], label="真实性")

                        score_submit_btn = gr.Button("保存")
                        output = gr.Textbox(label="保存结果")

                        score_submit_btn.click(
                            fn=process_form,
                            inputs=[logic_score, prof_score, empathy_score, authentic_score, scores, model_id],
                            outputs=output
                        )
                        # score_submit_btn.click(
                        #     update_dataframe,
                        #     inputs=scores,
                        #     outputs=df
                        # )
        gr.Markdown("\n# ")
        gr.Markdown("\n\n# 请更新并查看已保存分数并在最后进行整体分数提交")
        df = gr.Dataframe(
            value=default_dataframe_value,
            row_count=(4, "fixed"),
            col_count=(5, "fixed"),
        )

        with gr.Row():
            score_status_submit_btn = gr.Button("刷新已评估分数")
            whole_submit_btn = gr.Button("提交整个评价结果")
        output = gr.Textbox(label="提交结果")
        # 绑定按钮点击事件
        score_status_submit_btn.click(
            update_dataframe,
            inputs=scores,
            outputs=df
        )
        whole_submit_btn.click(
            on_whole_submit,
            inputs=[scores, df],
            outputs=output
        )
    demo.queue().launch(
        share=args.share,
        inbrowser=args.inbrowser,
        server_port=args.server_port,
        server_name=args.server_name,
    )


def main():
    args = _get_args()

    _launch_demo(args)


if __name__ == '__main__':
    main()
