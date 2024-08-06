from typing import Optional, Iterable, Dict, Any, Callable
from openai.types.chat import ChatCompletionMessageParam
from typing_extensions import Literal
from baselines.chat_CPsyCounX import chat_with_CPsyCounX
from baselines.chat_PsyChat import chat_with_PsyChat
from baselines.chat_Qwen import chat_with_Qwen_counselor
from SuDoSys.chat import chat_with_SuDoSys
from utils.chat_GLM4 import chat_with_GLM4_client


def chat(model: Literal["Qwen2-7B-Counselor", "PsyChat", "CPsyCounX", "SoDuSys", "GLM4-9B-Client"],
         message: Iterable[ChatCompletionMessageParam],
         cache: Optional[dict] = None,
         ):
    result_func = Callable[[Iterable[ChatCompletionMessageParam], Optional[dict]], Any]
    model_handlers: Dict[
        Literal["Qwen2-7B-Counselor", "PsyChat", "CPsyCounX", "SoDuSys", "GLM4-9B-Client"], result_func] = {
        "Qwen2-7B-Counselor": lambda msg, _cache: handle_qwen2(msg, cache),
        "PsyChat": lambda msg, _cache: handle_psychat(msg, cache),
        "CPsyCounX": lambda msg, _cache: handle_cpsycoun(msg, cache),
        "SoDuSys": lambda msg, _cache: handle_sudosys(msg, cache),
        "GLM4-9B-Client": lambda msg, _cache: handle_glm4(msg, cache),
    }

    def handle_qwen2(_message: Iterable[ChatCompletionMessageParam], _: None) -> Any:
        # 处理Qwen2(Baseline)模型的逻辑
        print(f"Handling Qwen2 model")
        response = chat_with_Qwen_counselor(_message)
        return response, None

    def handle_psychat(_message: Iterable[ChatCompletionMessageParam], _: None) -> Any:
        # 处理PsyChat模型的逻辑
        print(f"Handling PsyChat model")
        response = chat_with_PsyChat(_message)
        return response, None

    def handle_cpsycoun(_message: Iterable[ChatCompletionMessageParam], _: None) -> Any:
        # 处理CPsyCoun模型的逻辑
        print(f"Handling CPsyCounX model")
        response = chat_with_CPsyCounX(_message)
        return response, None

    def handle_sudosys(_message: Iterable[ChatCompletionMessageParam], _cache: dict) -> Any:
        print(f"Handling SuDoSys")
        response, _cache = chat_with_SuDoSys(_message, _cache)
        return response, _cache

    def handle_glm4(_message: Iterable[ChatCompletionMessageParam], portrait: dict) -> Any:
        print(f"Handling GLM-4-9B")
        response, _ = chat_with_GLM4_client(_message, portrait)
        return response, _

    handler = model_handlers.get(model)
    if handler is None:
        # 不存在的模型处理
        raise ValueError(f"Unsupported model: {model}")
    return handler(message, cache)
