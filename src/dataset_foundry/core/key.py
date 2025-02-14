class Key:
    """
    A key that represents the path to a value within a dictionary instead of the value itself.
    """
    path: str

    def __init__(self, path: str):
        self.path = path
