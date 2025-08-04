import pytest
from unittest.mock import MagicMock

from dataset_foundry.actions.item.foreach_item_element import foreach_item_element
from dataset_foundry.core.dataset_item import DatasetItem
from dataset_foundry.core.context import Context
from dataset_foundry.core.key import Key

@pytest.mark.asyncio
async def test_foreach_item_element_basic():
    item = DatasetItem("test_id", {
        "numbers": [1, 2, 3],
        "results": []
    })
    context = MagicMock()
    seen = []
    async def record_action(item, context):
        seen.append((item.data.get("element"), item.data.get("index")))
    foreach_action = foreach_item_element(
        collection=Key("numbers"),
        actions=[record_action]
    )
    await foreach_action(item, context)
    assert seen == [(1, 0), (2, 1), (3, 2)]

@pytest.mark.asyncio
async def test_foreach_item_element_custom_keys():
    item = DatasetItem("test_id", {
        "strings": ["a", "b"],
        "results": []
    })
    context = MagicMock()
    seen = []
    async def record_action(item, context):
        seen.append((item.data.get("element"), item.data.get("index")))
    foreach_action = foreach_item_element(
        collection=Key("strings"),
        actions=[record_action]
    )
    await foreach_action(item, context)
    assert seen == [("a", 0), ("b", 1)]

@pytest.mark.asyncio
async def test_foreach_item_element_non_iterable():
    item = DatasetItem("test_id", {
        "not_a_list": "string"
    })
    context = MagicMock()
    async def record_action(item, context):
        pass  # This should not be called
    foreach_action = foreach_item_element(
        collection=Key("not_a_list"),
        actions=[record_action]
    )
    with pytest.raises(ValueError, match="'collection' is not iterable"):
        await foreach_action(item, context)

@pytest.mark.asyncio
async def test_foreach_item_element_empty_collection():
    item = DatasetItem("test_id", {
        "empty_list": []
    })
    context = MagicMock()
    seen = []
    async def record_action(item, context):
        seen.append(item.data.get("element"))
    foreach_action = foreach_item_element(
        collection=Key("empty_list"),
        actions=[record_action]
    )
    await foreach_action(item, context)
    assert seen == []

@pytest.mark.asyncio
async def test_foreach_item_element_parent_reference():
    item = DatasetItem("test_id", {
        "numbers": [1, 2],
        "results": []
    })
    context = MagicMock()
    seen = []
    async def record_action(item, context):
        seen.append((item.data.get("element"), item.data.get("parent")))
    foreach_action = foreach_item_element(
        collection=Key("numbers"),
        actions=[record_action]
    )
    await foreach_action(item, context)
    assert len(seen) == 2
    assert seen[0][0] == 1
    assert seen[1][0] == 2
    # Check that parent references point to the original item
    assert seen[0][1] is item
    assert seen[1][1] is item

@pytest.mark.asyncio
async def test_foreach_item_element_item_id_generation():
    item = DatasetItem("test_id", {
        "numbers": [1, 2],
        "results": []
    })
    context = MagicMock()
    seen_ids = []
    async def record_action(item, context):
        seen_ids.append(item.id)
    foreach_action = foreach_item_element(
        collection=Key("numbers"),
        actions=[record_action]
    )
    await foreach_action(item, context)
    assert seen_ids == ["test_id_0", "test_id_1"]