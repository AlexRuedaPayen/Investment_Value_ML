import os
import json

class DotDict:
    """A dictionary that supports dot notation."""

    def __init__(self, path):
        if isinstance(path,dict):
            self.main=path
        if isinstance(path,str):
            with open(path) as file:
                self.main = json.load(file)  # Load JSON data directly, no need for DotDict recursion

    def __getattr__(self, name):
        # Handle the case where 'name' doesn't exist in the dict
        if name in self.main:
            value = self.main[name]
            # If the value is a dictionary, return a new DotDict instance
            if isinstance(value, dict):
                return DotDict(value)
            return value
        else:
            raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")




def create_local_file(file_path, content):
    """
    Create a file with the given content.
    """
    with open(file_path, 'w') as f:
        f.write(content)
    print(f"File {file_path} created successfully.")



def remove_local_file(file_path):
    """
    Remove a local file.
    """
    if os.path.exists(file_path):
        os.remove(file_path)
        print(f"Local file {file_path} removed successfully.")
    else:
        print(f"Local file {file_path} does not exist.")

