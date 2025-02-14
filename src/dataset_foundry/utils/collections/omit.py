from toolz import keyfilter

def omit(denylist, dictionary):
    """
    Omit keys from a dictionary.

    Args:
        denylist (list): A list of keys to omit from the dictionary.
        dictionary (dict): The dictionary to omit keys from.

    Returns:
        dict: A new dictionary with the specified keys omitted.
    """
    return keyfilter(lambda k: k not in denylist, dictionary)
