import argparse
from fastapi import FastAPI, Body
from pydantic import BaseModel
from model_class import CPsyCounX
import asyncio

app = FastAPI()


class CompletionRequest(BaseModel):
    query: str
    history: list[str]


# 创建一个全局锁
lock = asyncio.Lock()


@app.post("/v1/completions")
async def completions(request: CompletionRequest = Body(...)):
    # history is a list of strings
    async with lock:
        query = request.query
        history = request.history
        in_history, tmp = [], []
        for idx, item in enumerate(history):
            if idx % 2 == 0:
                tmp = item
            else:
                in_history.append((tmp, item))
        print(f"Received query: {query}")
        print(f"Received history: {history}")

        response, history = model.chat_once(query, in_history)
        print(history)

        print(f"Generated response: {response}")

        return {"message": "Received completion request.", "response": response}


# 如果需要在生产环境中使用，可以使用下面的代码启动服务器
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Specify configurations.")
    parser.add_argument("--device", type=str, default='cuda',
                        help="Device to use for computation (e.g., 'cuda:0', 'cuda:1')")
    parser.add_argument("--port", type=int, default=8010,
                        help="Device to use for computation (e.g., 'cuda:0', 'cuda:1')")
    args = parser.parse_args()
    print(f"Using device: {args.device}")
    model = CPsyCounX(args.device)

    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=args.port)
