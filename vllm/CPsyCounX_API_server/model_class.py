import argparse
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
# Set `torch_dtype=torch.float16` to load model in float16, otherwise it will be loaded as float32 and cause OOM Error.


class CPsyCounX:
    def __init__(self, device="cuda"):
        self.device = device
        self.tokenizer = AutoTokenizer.from_pretrained("CPsyCounX", trust_remote_code=True)

        self.chat_history = []
        self.model = AutoModelForCausalLM.from_pretrained("CPsyCounX", torch_dtype=torch.float16,
                                                          trust_remote_code=True).to(self.device).eval()

    def chat_once(self, query, history):
        response, history = self.model.chat(self.tokenizer, query, history=history)

        return response, history

    def chat_once_streaming(self, query, history):
        length = 0
        final_response, final_history = '', ''
        for response, history in self.model.stream_chat(self.tokenizer, query, history=history):
            print(response[length:], flush=True, end="")
            length = len(response)
            final_response = response
            final_history = history
        print()
        return final_response, final_history

    def cmd_chat(self):
        print("输入'quit'以退出，输入'clear'以清空聊天记录")
        response, history = self.model.chat(self.tokenizer, "咨询师你好", history=[])
        print('CPsyCounX：' + str(response))
        query = input('用户：')
        while query != 'quit':
            if query == 'clear':
                history = []
                query = "咨询师你好"
                print("聊天记录已清空")
            # response, history = self.chat_once_streaming(query, history)
            response, history = self.chat_once(query, history)
            print('CPsyCounX：' + str(response))
            query = input('用户：')
        exit()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Specify a device for computation.")
    parser.add_argument("--device", type=str, default='cuda',
                        help="Device to use for computation (e.g., 'cuda:0', 'cuda:1')")

    args = parser.parse_args()
    print(f"Using device: {args.device}")
    model = CPsyCounX(args.device)
    model.cmd_chat()
