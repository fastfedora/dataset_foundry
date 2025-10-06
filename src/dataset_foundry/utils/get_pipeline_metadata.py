from ..core.context import Context

def get_pipeline_metadata(context: Context) -> dict:
    """
    Get the metadata for the active pipeline.
    """
    parent_metadata = get_pipeline_metadata(context.parent) if context.parent else None

    return {
        "name": context.pipeline.name,
        **context.pipeline.metadata,
        **({ "parent": parent_metadata } if parent_metadata else {}),
    }
