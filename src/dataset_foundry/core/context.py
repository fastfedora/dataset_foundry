class Context(dict):
    """
    A context object that can be used to store and retrieve data.
    """
    def __init__(self, values: dict = None):
        super().__init__()
        if values:
            self.update(values)
