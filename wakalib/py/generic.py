"""
This is a module to extend the functionality of Python.
"""
import datetime
import random
import string

from wakalib.exceptions.exception import ArgsError
from wakalib.py._str_to_datetime import (
    _get_timezone,
    _separate_date,
    _separate_micro_second,
    _separate_time,
)


class NonDupulicateStringsGenerator:
    """
    Instantiating generates a random string with no dupulicates.
    For example, use the following.

    string_generator = NonDupulicateStringsGenerator()
    random_string = next(string_generator)
    """

    def __init__(self, string_length: int = 20, max_generation: int = 50) -> None:
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
                argument_name="string_length",
                add="string_length must be an integer greater than or equal to 1.",
            )
        if max_generation <= 0:
            raise ArgsError(
                argument_name="max_generation",
                add="max_generation must be an integer greater than or equal to 1.",
            )
        if len(string.ascii_letters) ** string_length < max_generation:
            raise ArgsError(
                argument_name="max_generation",
                add=(
                    "The value is set to a value greater than the number that "
                    "can be generated with the specified string_length.\n"
                    f"HINT: can be generated with {string_length} charactes is "
                    f"{len(string.ascii_letters) ** string_length}."
                ),
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
                argument_name="string_length",
                add="string_length must be an integer greater than or equal to 1.",
            )
        self.__string_length = string_length

    @max_generation.setter
    def max_generation(self, max_generation: int) -> None:
        if max_generation <= 0:
            raise ArgsError(
                argument_name="max_generation",
                add="max_generation must be an integer greater than or equal to 1.",
            )
        if len(string.ascii_letters) ** self.string_length < max_generation:
            raise ArgsError(
                argument_name="max_generation",
                add=(
                    "The value is set to a value greater than the number that "
                    "can be generated with the specified string_length.\n"
                    f"HINT: can be generated with {self.string_length} charactes is "
                    f"{len(string.ascii_letters) ** self.string_length}."
                ),
            )
        self.__max_generation = max_generation

    def __iter__(self):
        return self

    def __next__(self) -> str:
        if self.count > self.max_generation:
            raise StopIteration()
        _random_string = self.get_random_string(string_length=self.string_length)
        while _random_string in self.generated_strings:
            _random_string = self.get_random_string(string_length=self.string_length)
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
        return "".join(
            [random.choice(string.ascii_letters) for _ in range(string_length)]
        )


def str_to_datetime(str_datetime: str) -> datetime:
    """
    ## Summary
    Convert string to date type.

    ## Args:
    - str_datetime (str):
        datetime-like string

    ## Returns:
    - datetime:
        If a converted datetime.
    """
    _date, _str = _separate_date(str_datetime)
    _time, _str = _separate_time(_str)
    if _time is None:
        return _date
    _date = _date.replace(hour=_time.hour, minute=_time.minute, second=_time.second)
    _micro_second, _str = _separate_micro_second(_str)
    if _micro_second is not None:
        _date = _date.replace(microsecond=_micro_second.microsecond)
    _timezone = _get_timezone(_str)
    if _timezone is None:
        return _date
    return _date.replace(tzinfo=_timezone)
