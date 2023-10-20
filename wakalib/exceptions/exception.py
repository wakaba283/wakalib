"""
Combining exception classes in one place facilitates error handling.
"""

class ArgsError(Exception):  # pylint: disable=missing-class-docstring
    def __init__(self, argument_name: str, add: str | None = None):
        self.argument_name = argument_name
        self.add = add
    def __str__(self):
        __base_text = (
            f'There is a problem with the argument. args: {self.argument_name}'
        )
        if self.add:
            return f'{__base_text} note: {self.add}'
        else:
            return __base_text


class FailedToConvert(Exception):  # pylint: disable=missing-class-docstring
    def __init__(self, css: str | None):
        self.css = css
    def __str__(self):
        if self.css:
            return 'Failed to convert. Check your HTML or CSS.'
        else:
            return 'Failed to convert. Check you HTML.'


class FilePathDoesNotExists(Exception):  # pylint: disable=missing-class-docstring
    def __init__(self, file_path: str):
        self.file_path = file_path
    def __str__(self):
        return f'{self.file_path} does not exists.'


class FilePathIsNotFile(Exception):  # pylint: disable=missing-class-docstring
    def __init__(self, file_path: str):
        self.file_path = file_path
    def __str__(self):
        return f'{self.file_path} is not file path.'
