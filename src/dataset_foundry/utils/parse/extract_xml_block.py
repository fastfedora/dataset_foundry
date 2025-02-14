def extract_xml_block(text: str, tag: str):
    """
    Extract a block of text from a string based on an XML start and end tag.

    Args:
        text: The string to extract the block from.
        tag: The tag to extract the block from.

    Returns:
        The block of text between the start and end tags.
    """
    start_marker = f"<{tag}>"
    end_marker = f"</{tag}>"
    start_index = text.find(start_marker)

    if start_index != -1:
        start_index += len(start_marker)
        end_index = text.find(end_marker, start_index)
        if end_index != -1:
            return text[start_index:end_index].strip()
        else:
            return text[start_index:].strip()
    else:
        return text
