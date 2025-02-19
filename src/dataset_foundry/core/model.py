from langchain.chat_models.base import BaseChatModel
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic

MAX_TOKENS = 8096

class Model:
    """
    A model that can be used to generate text.
    """
    @staticmethod
    def parse_model_string(model_string: str) -> tuple[str, str]:
        """Parse a model string in the format 'provider/model_name'."""
        try:
            provider, model_name = model_string.split("/")
            return provider, model_name
        except ValueError:
            raise ValueError(
                f"Invalid model format: {model_string}. "
                "Expected format: 'provider/model_name' (e.g., 'openai/gpt-4-turbo' or 'anthropic/claude-3-sonnet')"
            )

    @staticmethod
    def create(model: str, temperature: float) -> BaseChatModel:
        """Create a chat model instance based on the provider:model string."""
        provider, model_name = Model.parse_model_string(model)

        if provider == "openai":
            return ChatOpenAI(
                model=model_name,
                temperature=temperature
            )
        elif provider == "anthropic":
            return ChatAnthropic(
                model=model_name,
                temperature=temperature,
                max_tokens=MAX_TOKENS
            )
        else:
            raise ValueError(f"Unsupported model provider: {provider}")