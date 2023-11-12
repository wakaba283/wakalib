# pylint: disable=missing-module-docstring
from datetime import datetime, timezone, timedelta
from typing import Any, TypedDict
from types import MappingProxyType
import re


def _protect(__val: Any) -> MappingProxyType:
    if isinstance(__val, dict):
        for _key, _value in __val.items():
            __val[_key] = _protect(_value)
        return MappingProxyType(__val)
    if isinstance(__val, (tuple, list)):
        return tuple([_protect(_item) for _item in __val])
    return __val


class _PetternFormat(TypedDict):
    pattern: str
    format_: str


class _Pattern(TypedDict):
    date: tuple[_PetternFormat]
    time: tuple[_PetternFormat]
    micro_second: tuple[_PetternFormat]


class _ConstStrToDatetime:
    SEPARATOR: tuple = (" ", "T")
    PATTERN: _Pattern = _protect(
        {
            "date": (
                {
                    "pattern": r"[0-9]{4}/(0[1-9]|[1-9]|1[0-2])/(0[1-9]|[1-9]|[12][0-9]|3[01])",
                    "format_": r"%Y/%m/%d",
                },
                {
                    "pattern": r"[0-9]{4}-(0[1-9]|[1-9]|1[0-2])-(0[1-9]|[1-9]|[12][0-9]|3[01])",
                    "format_": r"%Y-%m-%d",
                },
                {
                    "pattern": r"(0[1-9]|[1-9]|[12][0-9]|3[01])\.(0[1-9]|[1-9]|1[0-2])\.[0-9]{4}",
                    "format_": r"%d.%m.%Y",
                },
                {
                    "pattern": r"(0[1-9]|[1-9]|[12][0-9]|3[01])/(0[1-9]|[1-9]|1[0-2])/[0-9]{4}",
                    "format_": r"%d/%m/%Y",
                },
                {
                    "pattern": r"(0[1-9]|[1-9]|[12][0-9]|3[01])/(0[1-9]|[1-9]|1[0-2])/[0-9]{2}",
                    "format_": r"%d/%m/%y",
                },
            ),
            "time": (
                {
                    "pattern": r"(0[0-9]|[0-9]|1[0-9]|2[0-4]):(0[0-9]|[0-9]|[1-5][0-9]):(0[0-9]|[0-9]|[1-5][0-9])",  # pylint: disable=line-too-long
                    "format_": r"%H:%M:%S",
                },
            ),
            "micro_second": ({"pattern": r"\.[0-9]{1,6}", "format_": r".%f"},),
        }
    )


def _separate_date(_val: str) -> tuple[datetime, str]:
    for _pattern in _ConstStrToDatetime.PATTERN["date"]:
        _match_datetime: re.Match | None = re.search(
            pattern=_pattern["pattern"],
            string=_val,
        )
        if _match_datetime is not None:
            _format = _pattern["format_"]
            break
    if not isinstance(_match_datetime, re.Match):
        raise ValueError("There is no year, month, date pattern.")
    _s, _e = _match_datetime.span()
    return (
        datetime.strptime(_val[_s:_e], _format),
        f"{_val[:_s]}{_val[_e:]}",
    )


def _separate_time(_val: str) -> tuple[datetime | None, str]:
    for _pattern in _ConstStrToDatetime.PATTERN["time"]:
        _match_datetime: re.Match | None = re.search(
            pattern=_pattern["pattern"],
            string=_val,
        )
        if _match_datetime is not None:
            _format = _pattern["format_"]
            break
    if not isinstance(_match_datetime, re.Match):
        return (None, _val)
    _s, _e = _match_datetime.span()
    return (
        datetime.strptime(_val[_s:_e], _format),
        f"{_val[:_s]}{_val[_e:]}",
    )


def _separate_micro_second(_val: str) -> tuple[datetime | None, str]:
    for _pattern in _ConstStrToDatetime.PATTERN["micro_second"]:
        _match_datetime: re.Match | None = re.search(
            pattern=_pattern["pattern"],
            string=_val,
        )
        if _match_datetime is not None:
            _format = _pattern["format_"]
            break
    if not isinstance(_match_datetime, re.Match):
        return (None, _val)
    _s, _e = _match_datetime.span()
    return (
        datetime.strptime(_val[_s:_e], _format),
        f"{_val[:_s]}{_val[_e:]}",
    )


def _get_timezone(_val: str) -> timezone | None:
    for _sep in _ConstStrToDatetime.SEPARATOR:
        _val = _val.replace(_sep, "")
    _match_datetime: re.Match | None = re.search(
        pattern="Z",
        string=_val,
    )
    if _match_datetime:
        return timezone.utc
    _match_datetime: re.Match | None = re.search(
        pattern=r"\+[0-9]{1,4}",
        string=_val,
    )
    if _match_datetime:
        _s, _e = _match_datetime.span()
        _str_timezone_int: str = _val[_s:_e].replace("+", "")
        if len(_str_timezone_int) in (1, 2):
            return timezone(offset=timedelta(hours=int(_str_timezone_int)))
        return timezone(
            offset=timedelta(
                hours=int(_str_timezone_int[:2]), minutes=int(_str_timezone_int[2:])
            )
        )
    return None
