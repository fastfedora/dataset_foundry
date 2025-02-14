from typing import Callable, Optional, Union
import json

from ...core.context import Context
from ...core.dataset_item import DatasetItem
from ...core.key import Key
from ...utils.params.resolve_item_value import resolve_item_value
from ...utils.parse.extract_code_block import extract_code_block
from ...utils.parse.extract_xml_block import extract_xml_block

def parse_item(
        input: Optional[Union[Callable,Key,str]] = Key("output"),
        output_key: Optional[Union[Callable,Key,str]] = None,
        parser: Optional[Union[Callable,Key,str]] = Key("parser"),
        code_block: Optional[Union[Callable,Key,str]] = None,
        xml_block: Optional[Union[Callable,Key,str]] = None,
    ):

    async def parse_item_action(item: DatasetItem, context: Context):
        resolved_parser = resolve_item_value(parser, item, context)
        resolved_code_block = resolve_item_value(code_block, item, context)
        resolved_xml_block = resolve_item_value(xml_block, item, context)
        resolved_output_key = resolve_item_value(output_key, item, context)

        if resolved_parser:
            output = resolved_parser(item, context)
        else:
            resolved_input = resolve_item_value(input, item, context, required_as="input")

            if resolved_code_block:
                output = extract_code_block(resolved_input, resolved_code_block)

                # TODO: Implement this better, so it's not hidden. [fastfedora 10.Feb.25]
                if resolved_code_block == 'json':
                    output = json.loads(output)
            elif resolved_xml_block:
                output = extract_xml_block(resolved_input, resolved_xml_block)
            else:
                raise ValueError("One of 'parser', 'code_block' or 'xml_block' are required")

        if resolved_output_key:
            item.push({ resolved_output_key: output }, parse_item);
        else:
            item.push(output, parse_item);

    return parse_item_action
