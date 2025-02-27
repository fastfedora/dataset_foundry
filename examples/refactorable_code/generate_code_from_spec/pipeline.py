from pathlib import Path
from typing import Any, Optional
from pydantic import BaseModel, Field
import yaml

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser

from dataset_foundry.actions.dataset.load_dataset import load_dataset
from dataset_foundry.actions.dataset.load_context import load_context
from dataset_foundry.actions.dataset.load_context import load_context
from dataset_foundry.actions.item.generate_item import generate_item
from dataset_foundry.actions.item.save_item_chat import save_item_chat
from dataset_foundry.actions.item.parse_item import parse_item
from dataset_foundry.actions.item.save_item import save_item
from dataset_foundry.core.context import Context
from dataset_foundry.core.dataset_item import DatasetItem
from dataset_foundry.core.item_pipeline import ItemPipeline
from dataset_foundry.utils.collections.omit import omit
from dataset_foundry.utils.get_model_fields import get_model_fields

class CodeSample(BaseModel):
    """A code sample that needs refactoring."""
    id: Optional[str] = None
    spec: Optional[Any] = None
    function_name: str = Field(description="The name of the function requiring refactoring")
    code: str = Field(description="The code that needs refactoring")
    language: str = Field(description="The programming language of the code")
    explanation: str = Field(description="Explanation of why the code needs refactoring")

fields = get_model_fields(CodeSample)
output_parser = PydanticOutputParser(pydantic_object=CodeSample)

def build_prompt(item: DatasetItem, context: Context):
    format_instructions = " - " + "\n - ".join(fields)
    prompt_template = ChatPromptTemplate.from_messages([
        ("user", context['prompts']['generate'])
    ])

    return prompt_template.partial(
        format_instructions=format_instructions,
        spec=yaml.dump(item.data),
        example=context['prompts']['refactor_example'],
    )

pipeline = ItemPipeline(
    name="generate_code_from_spec",
    setup=[
        load_context(dir=Path(__file__).parent, filename="config.yaml"),
        load_dataset(filename="specs.yaml", property="spec"),
    ],
    steps=[
        generate_item(prompt=build_prompt),
        save_item_chat(filename="chat_{id}.yaml"),
        parse_item(code_block="json"),
        save_item(
            contents=(lambda item: item.data["code"]),
            filename="item_{id}_{function_name}.py"
        ),
        save_item(
            contents=(lambda item: {
                'id': item.id,
                **omit(['code', 'response', 'messages', 'output'], item.data),
            }),
            filename="item_{id}_{function_name}.json",
            format="json"
        ),
    ]
)
