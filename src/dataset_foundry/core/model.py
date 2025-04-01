from typing import List

from langchain.chat_models.base import BaseChatModel
from langchain_core.messages import BaseMessage
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic

MAX_TOKENS = 8096

class Model:
    _model: BaseChatModel

    def __init__(self, model: str, temperature: float = None):
        provider, model_name = Model._parse_model_string(model)

        if provider == "openai":
            args = {
                "model": model_name,
                **({
                    "temperature": temperature,
                } if temperature is not None and model_name not in ['o1-mini', 'o3-mini'] else {}),
            }
            self._model = ChatOpenAI(**args)
        elif provider == "anthropic":
            self._model = ChatAnthropic(
                model=model_name,
                temperature=temperature,
                max_tokens=MAX_TOKENS
            )
        else:
            raise ValueError(f"Unsupported model provider: {provider}")

    """
    A model that can be used to generate text.
    """
    @staticmethod
    def _parse_model_string(model_string: str) -> tuple[str, str]:
        """Parse a model string in the format 'provider/model_name'."""
        try:
            provider, model_name = model_string.split("/")
            return provider, model_name
        except ValueError:
            raise ValueError(
                f"Invalid model format: {model_string}. "
                "Expected format: 'provider/model_name' (e.g., 'openai/gpt-4-turbo' or 'anthropic/claude-3-sonnet')"
            )

    async def ainvoke(self, messages: List[BaseMessage], **kwargs) -> BaseMessage:
        return await self._model.ainvoke(messages, **kwargs)
