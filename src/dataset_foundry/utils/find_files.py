import glob
from pathlib import PosixPath
import re
from typing import List, Optional, Union

class CompiledGlobPattern:
    glob: str
    regex: str
    variables: List[str]

def extract_variables(template: str, variable_regex: str, default_pattern: str = '[^/]+'):
    matches = re.findall(variable_regex, template)
    variables = []

    for match in matches:
        if '|' in match:
            name, pattern = match.split('|', 1)
        else:
            name = match
            pattern = default_pattern

        variables.append({
            'name': name,
            'pattern': pattern,
        })

    return variables

def compile_pattern(template: Union[str,PosixPath]) -> CompiledGlobPattern:
    template = str(template)

    variable_regex = r'\{([^}]+)\}'
    variables = extract_variables(template, variable_regex)

    # Replace unnamed glob elements
    regex_pattern = template.replace('.', r'\.').replace('*', r'.*?')

    # Convert pattern with {vars} to regex capture groups
    for variable in variables:
        regex_pattern = re.sub(r'\{[^}]+\}', f'({variable['pattern']})', regex_pattern, count=1)

    result = CompiledGlobPattern()
    result.glob = re.sub(variable_regex, '*', template)
    result.regex = re.compile(regex_pattern)
    result.variables = [variable['name'] for variable in variables]

    return result

def find_files(include_path: str, exclude_path: Optional[str]):
    """
    Find files matching the given path pattern and extract metadata from the path.

    Args:
        path: A Path object or string representing the file pattern to match

    Returns:
        list: List of dicts containing file paths and their extracted metadata
    """
    include_pattern = compile_pattern(include_path)
    exclude_pattern = compile_pattern(exclude_path) if exclude_path else None
    matching_files = glob.glob(include_pattern.glob)
    file_metadata = []

    for file_path in matching_files:
        include_match = include_pattern.regex.match(file_path)
        exclude_match = exclude_pattern.regex.match(file_path) if exclude_pattern else False

        if include_match and not exclude_match:
            captures = {}
            for name, value in zip(include_pattern.variables, include_match.groups()):
                captures[name] = value

            file_metadata.append({
                'path': file_path,
                'metadata': captures
            })

    file_metadata.sort(key=lambda x: x['path'])

    return file_metadata