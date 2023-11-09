"""
This is a module to extend the functionality of Python.
"""
import datetime
import json
import os
import random
import re
import string
from typing import Any, TypedDict, Union

from wakalib.exceptions.exception import ArgsError


class NonDupulicateStringsGenerator:
    """
    Instantiating generates a random string with no dupulicates.
    For example, use the following.

    string_generator = NonDupulicateStringsGenerator()
    random_string = next(string_generator)
    """
    def __init__(
            self,
            string_length: int = 20,
            max_generation: int = 50
        ) -> None:
        """
        ## Summary
        You can specify the length of the string to be generated and
        the maximum number of strings to be generated.

        ## Args:
        - string_length (int, optional): Defaults to 20.
        - max_generation (int, optional): Defaults to 50.
        """
        if string_length <= 0:
            raise ArgsError(
                argument_name='string_length',
                add='string_length must be an integer greater than or equal to 1.'
            )
        if max_generation <= 0:
            raise ArgsError(
                argument_name='max_generation',
                add='max_generation must be an integer greater than or equal to 1.'
            )
        if len(string.ascii_letters) ** string_length < max_generation:
            raise ArgsError(
                argument_name='max_generation',
                add=(
                    'The value is set to a value greater than the number that '
                    'can be generated with the specified string_length.\n'
                    f'HINT: can be generated with {string_length} charactes is '
                    f'{len(string.ascii_letters) ** string_length}.'
                )
            )
        self.__string_length = string_length
        self.__max_generation = max_generation
        self.__counter: int = 0
        self.__generated_strings: set = set()

    @property
    def string_length(self) -> int:  # pylint: disable=missing-function-docstring
        return self.__string_length

    @property
    def max_generation(self) -> int:  # pylint: disable=missing-function-docstring
        return self.__max_generation

    @property
    def count(self) -> int:  # pylint: disable=missing-function-docstring
        return self.__counter

    @property
    def generated_strings(self) -> set:  # pylint: disable=missing-function-docstring
        return self.__generated_strings

    @string_length.setter
    def string_length(self, string_length: int) -> None:
        if string_length <= 0:
            raise ArgsError(
                argument_name='string_length',
                add='string_length must be an integer greater than or equal to 1.'
            )
        self.__string_length = string_length

    @max_generation.setter
    def max_generation(self, max_generation: int) -> None:
        if max_generation <= 0:
            raise ArgsError(
                argument_name='max_generation',
                add='max_generation must be an integer greater than or equal to 1.'
            )
        if len(string.ascii_letters) ** self.string_length < max_generation:
            raise ArgsError(
                argument_name='max_generation',
                add=(
                    'The value is set to a value greater than the number that '
                    'can be generated with the specified string_length.\n'
                    f'HINT: can be generated with {self.string_length} charactes is '
                    f'{len(string.ascii_letters) ** self.string_length}.'
                )
            )
        self.__max_generation = max_generation

    def __iter__(self):
        return self

    def __next__(self) -> str:
        if self.count > self.max_generation:
            raise StopIteration()
        _random_string = self.get_random_string(
            string_length=self.string_length
        )
        while _random_string in self.generated_strings:
            _random_string = self.get_random_string(
                string_length=self.string_length
            )
        self.__generated_strings.add(_random_string)
        self.__counter += 1
        return _random_string

    @staticmethod
    def get_random_string(string_length: int) -> str:
        """
        ## Summary
        A single random string can be generated.

        ## Args:
        string_length (int): Number of characters to generate.

        ## Returns:
        str: Generated random string.
        """
        return ''.join(
            [random.choice(string.ascii_letters) for _ in range(string_length)]
        )


class _DictSub(TypedDict):
    pattern: str
    replace: str


class _DictFormat(TypedDict):
    pattern: str
    format: str
    sub: Union[_DictSub, None]


def str_to_datetime(
        str_datetime: str, _error: Any = True
    ) -> datetime.datetime | Any:
    """
    ## Summary
    Convert string to date type.
    Assumed string patterns can be added to resource/pattern.json as needed.

    ## Args:
    - str_datetime (str):
        datetime-like string
    - _error (Any, optional):
        Sets the behavior if the string does not match
        the expected string pattern.
        The default is True, in which case an exception is raised.
        To return an arbitrary value without causing harm, set here.

    ## Raises:
    - ValueError:
        If _error is not set, or if True is set, this exception will be raised.

    ## Returns:
    - datetime.datetime | Any:
        If a converted datetime or _error is set, that value is returned.
    """
    _json_path = \
        os.path.join(os.path.dirname(__file__), r'resource/pattern.json')
    with open(file=_json_path, mode='rt', encoding='utf-8') as file_:
        dict_pattern: dict[str, _DictFormat] = json.load(file_)
    for _dict_format in dict_pattern.values():
        if re.fullmatch(pattern=_dict_format['pattern'], string=str_datetime):
            if not _dict_format['sub']:
                return datetime.datetime.strptime(
                    str_datetime,
                    _dict_format['format']
                )
            return datetime.datetime.strptime(
                re.sub(
                    pattern=_dict_format['sub']['pattern'],
                    repl=_dict_format['sub']['replace'],
                    string=str_datetime
                ),
                _dict_format['format']
            )
    if not isinstance(_error, bool):
        return _error
    if _error is not True:
        return datetime.datetime(year=2000, month=1, day=1)
    raise ValueError('String will not match any pattern.')
