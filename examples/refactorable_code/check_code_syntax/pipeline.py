from dataset_foundry.actions.dataset.load_dataset_from_directory import load_dataset_from_directory
from dataset_foundry.actions.item.if_item import if_item
from dataset_foundry.actions.item.log_item import log_item
from dataset_foundry.actions.item.set_item_property import set_item_property
from dataset_foundry.actions.item.validate_code_syntax import validate_code_syntax
from dataset_foundry.core.item_pipeline import ItemPipeline
from dataset_foundry.core.key import Key
from dataset_foundry.core.template import Template

pipeline = ItemPipeline(
    name="check_code_syntax",
    metadata={
        "version": "0.1.0",
        "author": "fastfedora",
    },
    setup=[
        load_dataset_from_directory(include="{id}/info.yaml"),
        load_dataset_from_directory(include="{id}/source.py", property="code", merge=True),
    ],
    steps=[
        validate_code_syntax(input=Key("code"), output_key="code_syntax"),
        if_item("code_syntax['is_valid']", [
            set_item_property(key="valid_code", value="true"),
            if_item("context.log_level == 'debug'", [
                log_item(message=Template("{id}: code valid")),
            ]),
        ], [
            set_item_property(key="valid_code", value="false"),
            log_item(message=Template("{id}: code invalid: {code_syntax.syntax_error}")),
        ]),
    ]
)
