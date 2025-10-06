from typing import Optional


class ItemPipelineOptions:
    """
    Options for configuring ItemPipeline execution behavior.

    Attributes:
        max_concurrent_items: Maximum number of items to process concurrently.
            Defaults to 1 (sequential).
    """

    def __init__(self, max_concurrent_items: Optional[int] = 1):
        self.max_concurrent_items = max_concurrent_items
