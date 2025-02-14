def extract_code_block(text: str, format: str):
    """
    Extract a block of code from a string based on a code block start and end marker.

    Args:
        text: The string to extract the block from.
        format: The format of the code block to extract.

    Returns:
        The block of text between the start and end markers.
    """
    start_marker = f"```{format}"
    end_marker = "```"
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
