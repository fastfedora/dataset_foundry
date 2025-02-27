from typing import Callable, Union

from langchain_core.prompts import ChatPromptTemplate

from ...core.context import Context
from ...core.dataset_item import DatasetItem
from ...core.key import Key
from ...types.item_action import ItemAction
from ...utils.params.resolve_item_value import resolve_item_value
from ...utils.format.preprocess_template import preprocess_template

def build_prompt(user: str, variables: dict):
    user, variables = preprocess_template(user, variables)
    prompt_template = ChatPromptTemplate.from_template(user)
    return prompt_template.partial(**variables)

def generate_item(
        prompt: Union[Callable,Key,str] = Key("prompt"),
        model: Union[Callable,Key,str] = Key("model"),
    ) -> ItemAction:
    async def generate_item_action(item: DatasetItem, context: Context):
        resolved_prompt = resolve_item_value(prompt, item, context, required_as="prompt")
        resolved_model = resolve_item_value(model, item, context, required_as="model")

        if (isinstance(resolved_prompt, str)):
            resolved_prompt = build_prompt(resolved_prompt, { "id": item.id, **item.data })

        messages = await resolved_prompt.aformat_messages()
        response = await resolved_model.ainvoke(messages)

        item.push({
                "messages": messages,
                "response": response,
                "output": response.content,
        }, generate_item);

    return generate_item_action
