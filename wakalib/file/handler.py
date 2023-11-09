"""
This module is used for general file operations.
"""

import functools
import json
import mimetypes
import os
import tempfile
from typing import Callable, Literal


def get_file_type(
        filepath: str
    ) -> Literal['excel', 'word', 'powerpoint', 'pdf', 'unknown']:
    """
    ## Summary
    Return file type string.

    ## Description
    To add file types, edit mimetypes.json in the "resource" folder.

    ## Args:
    - filepath (str) :
        Path of the target file.

    ## Returns:
    - str: "excel", "word", "powerpoint", "pdf" or "unknown"
    """
    _json_mimetypes_path = \
        os.path.join(os.path.dirname(__file__), 'resource/mimetypes.json')
    with open(file=_json_mimetypes_path, mode='rt', encoding='utf-8') as file_:
        dict_mimetypes = json.load(file_)
    guess_mimetype = mimetypes.guess_type(filepath)[0]
    file_type = dict_mimetypes.get(guess_mimetype)
    if not file_type:
        file_type = 'unknown'
    return file_type


# Following function is used by decorator.
def create_folder(func: Callable):
    """
    ## Summary
    When this function is set in a decorator,
    the path of the temporary folder is passed as the first argument.

    ## Description
    If you have Pylint installed,
    the number of arguments does not match and an error will be displayd.
    "# pylint: disable=no-value-for-parameter"
    Note: I am continually considering changing this method if a better one is found.

    ## Args:
    - func (Callable):
        Function.
    """
    @functools.wraps(func)
    def _wrapper(*args, **kwargs):
        with tempfile.TemporaryDirectory() as directory_path:
            return func(directory_path, *args, **kwargs)
    return _wrapper
