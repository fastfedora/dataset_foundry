import datason.json as json
from pathlib import Path
import textwrap
from typing import Any, List, Union
import yaml

from langchain_core.messages import BaseMessage

def format_content(content: str) -> Any:
    """Format content, converting JSON strings to objects and handling multiline text."""
    if content.strip().startswith("```json"):
        json_str = content.split("```json")[1].split("```")[0].strip()
        try:
            return json.loads(json_str)
        except json.JSONDecodeError:
            pass
    return content

def wrap_text(text: str, max_characters: int = 100) -> str:
    """Wrap text at 100 characters, preserving existing line breaks."""
    # Split text into lines; we'll add the linefeed back in below to preserve paragraph breaks
    lines = text.split('\n')

    # Wrap each line individually
    wrapped_lines = []

    for line in lines:
        # PyYAML silently uses quoted style if the text has any tab characters or newlines with
        # whitespace before them, since YAML can't represent these in block literals. But for the
        # messages, we don't care about these two cases, so we remove/convert them.
        line = line.rstrip().replace("\t"," " * 4)
        if len(line) > max_characters:
            wrapped_lines.extend(textwrap.wrap(line, width=max_characters))
        else:
            wrapped_lines.append(line)

    return '\n'.join(wrapped_lines)

def should_use_literal_block(text: str) -> bool:
    """Determine if text should use YAML literal block style."""
    return len(text) > 50 or '\n' in text

# Configure yaml to use literal block style for long/multiline strings
class literal_str(str): pass

def literal_presenter(dumper, data):
    return dumper.represent_scalar('tag:yaml.org,2002:str', wrap_text(data), style='|')

yaml.add_representer(literal_str, literal_presenter)

def save_messages(file: Union[str, Path], messages: List[BaseMessage], response_content: str = None):
    """Save chat messages to a YAML file with proper formatting for readability.

    Args:
        file: Path to save the YAML file
        messages: List of chat messages
        response_content: Optional final response from assistant
    """
    # Format messages with appropriate string handling
    chat_log = {
        'messages': [
            {
                'role': message.type,
                'content': literal_str(message.content) if should_use_literal_block(message.content)
                         else format_content(message.content)
            }
            for message in messages
        ]
    }

    # Add final response if provided
    if response_content is not None:
        chat_log['messages'].append({
            'role': 'assistant',
            'content': literal_str(response_content) if should_use_literal_block(response_content)
                     else format_content(response_content)
        })

    # Ensure parent directory exists
    file = Path(file)
    file.parent.mkdir(parents=True, exist_ok=True)

    # Save to file
    with open(file, 'w') as f:
        yaml.dump(chat_log, f, sort_keys=False, width=float("inf"))