from toolz import keyfilter

def pick(allowlist, dictionary):
    """
    Create a new dictionary with only the keys specified in allowlist.

    Args:
        allowlist (list): A list of keys to include from the dictionary.
        dictionary (dict): The dictionary to include keys from.

    Returns:
        dict: A new dictionary with only the specified keys.
    """
    return keyfilter(lambda key: key in allowlist, dictionary)
