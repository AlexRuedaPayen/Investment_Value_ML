import json

class DotDict:
    """A dictionary that supports dot notation."""

    def __init__(self,path):
        with open(path) as file:
            self.main = DotDict(json.load(file))

    def __getattr__(self, name):
        value = self.main[name]
        if isinstance(value, dict):
            return DotDict(value)
        return value
