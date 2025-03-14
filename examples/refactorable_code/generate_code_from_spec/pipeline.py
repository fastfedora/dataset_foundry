from pathlib import Path
from typing import Any, Optional
from pydantic import BaseModel, Field
import yaml

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser

from dataset_foundry.actions.dataset.load_dataset import load_dataset
from dataset_foundry.actions.item.generate_item import generate_item
from dataset_foundry.actions.item.save_item_chat import save_item_chat
from dataset_foundry.actions.item.set_item_metadata import set_item_metadata
from dataset_foundry.actions.item.set_item_property import set_item_property
from dataset_foundry.actions.item.parse_item import parse_item
from dataset_foundry.actions.item.save_item import save_item
from dataset_foundry.core.context import Context
from dataset_foundry.core.dataset_item import DatasetItem
from dataset_foundry.core.item_pipeline import ItemPipeline
from dataset_foundry.core.key import Key
from dataset_foundry.core.template import Template
from dataset_foundry.utils.collections.omit import omit
from dataset_foundry.utils.collections.pick import pick
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
    metadata={
        "version": "0.1.0",
        "author": "fastfedora",
        "description": "Generate code from a spec",
    },
    config=Path(__file__).parent / "config.yaml",
    setup=[
        load_dataset(
            filename="specs.yaml",
            property="spec",
            id_generator=lambda index, data: f"{index+1:03d}_{data['name']}",
        ),
    ],
    steps=[
        set_item_property(key="source", value="source.py"),
        set_item_metadata(),
        generate_item(prompt=build_prompt),
        save_item_chat(filename=Template("chat_{id}_generate_code_from_spec.yaml")),
        parse_item(code_block="json"),
        save_item(contents=Key("code"), filename=Template("{id}/{source}")),
        save_item(
            contents=(lambda item: {
                'id': item.id,
                'metadata': item.data['metadata'],
                'name': item.data['spec']['name'],
                'language': item.data['spec']['language'],
                **pick(['spec', 'source', 'test'], item.data),
            }),
            filename=Template("{id}/info.yaml"),
            format="yaml"
        ),
    ]
)
