import re
import logging
from typing import Callable, Optional, Union

from langchain_core.prompts import ChatPromptTemplate

from ...core.context import Context
from ...core.dataset import Dataset
from ...core.dataset_item import DatasetItem
from ...core.key import Key
from ...types.dataset_action import DatasetAction
from ...utils.params.resolve_dataset_value import resolve_dataset_value

variable_regex = r'\{([^}]+)\}'

logger = logging.getLogger(__name__)

def generate_dataset(
        prompt: Union[Callable,Key,str] = Key("prompt"),
        model: Union[Callable,Key,str] = Key("model"),
        parser: Optional[Union[Callable,Key,str]] = None,
        output_key: Optional[Union[Callable,Key,str]] = None,
    ) -> DatasetAction:
    async def generate_dataset_action(dataset: Dataset, context: Context):
        resolved_prompt = resolve_dataset_value(prompt, dataset, context, required_as="prompt")
        resolved_model = resolve_dataset_value(model, dataset, context, required_as="model")
        resolved_parser = resolve_dataset_value(parser, dataset, context)
        resolved_output_key = resolve_dataset_value(output_key, dataset, context)

        # Build the prompt
        variables = re.findall(variable_regex, resolved_prompt)
        prompt_template = ChatPromptTemplate.from_messages([ ("user", resolved_prompt) ])
        model_prompt = prompt_template.partial(
            **{variable: context[variable] for variable in variables},
        )

        # Generate the response
        messages = await model_prompt.aformat_messages()
        response = await resolved_model.ainvoke(messages)

        if resolved_parser:
            contents = resolved_parser(response.content)
        else:
            contents = [response.content]
            resolved_output_key = resolved_output_key or "output"

        if context['num_samples'] and len(contents) > context['num_samples']:
            logger.debug(f"Limiting dataset to {context['num_samples']} samples")
            contents = contents[:context['num_samples']]

        for i, content in enumerate(contents):
            item = DatasetItem(
                f"{i+1:03d}",
                { resolved_output_key: content } if resolved_output_key else content
            )
            dataset.add(item)

    return generate_dataset_action
