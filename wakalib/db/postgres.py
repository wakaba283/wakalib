"""
This module is a collection of database-related operations.
It uses the following libraries
- pandas
- psycopg2

Typical usage example:
    db_foo = DBHandling(
        credential_filepath = 'hoge/fuga.json'
        role = 'piyo/piyon'
    )
    db_foo.select_fetchone(...)

* Postgres and PostgreSQL are all registered trademarks of
the PostgreSQL Community Association of Canada.
"""

import asyncio
import json
import re
import warnings
from asyncio.tasks import Task
from collections import ChainMap
from dataclasses import dataclass
from typing import Any, Callable, Literal, NamedTuple, TypedDict, overload

import pandas as pd
import psycopg
from psycopg import Column, sql
from psycopg.sql import SQL

from wakalib.exceptions.exception import ArgsError
from wakalib.py.generic import NonDupulicateStringsGenerator


class _IsExstsParamsDictionary(TypedDict):
    target_column: str
    values: Any | list[Any]


class Where(NamedTuple):
    field: str
    value: Any
    operator: Literal["=", "<>", ">", "<", ">=", "<=", "in", "like"]


class Set(NamedTuple):
    field: str
    value: Any


@dataclass(frozen=True)
class MakeINSERT:
    """
    _summary_
    """

    table: str
    sets: Set | tuple[Set]


@dataclass(frozen=True)
class MakeSELECT:
    """
    _summary_
    """

    table: str
    fields: str | tuple[str]
    wheres: Where | tuple[Where] | None
    join: Literal["AND", "OR"] = "AND"
    method: Literal["fetchone", "fetchall"] = "fetchone"


SP_ALLOW_TABLES: tuple[str] = ("information_schema.columns",)


@dataclass(frozen=True)
class MakeUPDATE:
    """
    _summary_
    """

    table: str
    sets: Set | tuple[Set]
    wheres: Where | tuple[Where] | None
    join: Literal["AND", "OR"] = "AND"


@dataclass(frozen=True)
class MakeDELETE:
    """
    _summary_
    """

    table: str
    wheres: Where | tuple[Where] | None
    join: Literal["AND", "OR"] = "AND"


class DBHandling:
    """
    Set up and manipulate database credentials.
    """

    def __init__(self, credentials_filepath: str, role: str) -> None:
        """
        ## Summary
        select database and use role

        ## Args:
        - credentials_filepath (str) :
            Enter the credentials filepath.
        - role (str) :
            Enter the role you have set up. e.g. db/db_read

        ## Note
        The credentials file must be in a format such as
        {
            "db_name/role_name" (any):{
                "name": database name,
                "user": use role name,
                "password": use role passsword,
                "host": database address,
                "port": database port
            }
        }
        """
        self.__role: str = role
        with open(file=credentials_filepath, mode="rt", encoding="utf-8") as _file:
            credentials: dict[str, dict] = json.load(_file)
        if not credentials.get(role):
            raise ValueError(
                "The specified role name is not found in the credentials file."
            )
        self.__db_config: dict = credentials[role]
        self.__dict_make_sql_function: dict = {
            MakeINSERT: self._make_sub_insert_sql,
            MakeSELECT: self._make_sub_select_sql,
            MakeUPDATE: self._make_sub_update_sql,
            MakeDELETE: self._make_sub_delete_sql,
        }

    @property
    def role(self) -> str:  # pylint: disable=missing-function-docstring
        return self.__role

    @property
    def _db_config(self) -> dict:  # pylint: disable=missing-function-docstring
        return self.__db_config

    @property
    def _dict_make_sql_function(
        self,
    ) -> dict:  # pylint: disable=missing-function-docstring
        return self.__dict_make_sql_function

    def _get_connection(self):
        return psycopg.AsyncConnection.connect(
            dbname=self._db_config["name"],
            user=self._db_config["user"],
            password=self._db_config["password"],
            host=self._db_config["host"],
            port=self._db_config["port"],
        )

    # Future: Deleted
    def _get_connection_old(self) -> psycopg.Connection:
        warnings.warn(
            message="This method will be discontinued in the future.",
            category=FutureWarning,
        )
        return psycopg.connect(
            dbname=self._db_config["name"],
            user=self._db_config["user"],
            password=self._db_config["password"],
            host=self._db_config["host"],
            port=self._db_config["port"],
        )

    # Future: Deleted
    def select_fetchone(
        self,
        sql: str,  # pylint: disable=redefined-outer-name
        params: dict[str, Any] | None = None,
    ) -> tuple:
        """
        ## Args:
        - sql (str):
            SQL string.
        - params (dict, optional):
            If you need to embed a variable, make the embedded value and
            the variable a dictionary type.

        ## Returns:
        - tuple: Search results are returned as a tuple.

        ## Example
        sql = "SELECT hoge from fuga WHERE piyo=%(piyo)s;"
        params = {'piyo': piyo}
        """
        warnings.warn(
            message="This method will be discontinued in the future.",
            category=FutureWarning,
        )
        with self._get_connection_old() as conn:  # pylint: disable=not-context-manager
            with conn.cursor() as cur:
                if params:
                    cur.execute(sql, params)
                else:
                    cur.execute(sql)
                data = cur.fetchone()
        return data

    # Future: Deleted
    def select_fetchall(
        self,
        sql: str,  # pylint: disable=redefined-outer-name
        params: dict[str, Any] | None = None,
    ) -> pd.DataFrame:
        """
        ## Args:
        - sql (str):
            SQL string.
        - params (dict, optional):
            If you need to embed a variable, make the embedded value and
            the variable a dictionary type.

        ## Returns:
        - pandas.Dataframe: Search results are returned as a pandas.Dataframe.

        ## Example
        sql = "SELECT * from fuga WHERE piyo=%(piyo)s;"
        params = {'piyo': piyo}
        """
        warnings.warn(
            message="This method will be discontinued in the future.",
            category=FutureWarning,
        )
        with self._get_connection_old() as conn:  # pylint: disable=not-context-manager
            with conn.cursor() as cur:
                if params:
                    cur.execute(sql, params)
                else:
                    cur.execute(sql)
                data = pd.DataFrame(
                    cur.fetchall(), columns=[col.name for col in cur.description]
                )
        return data

    # Future: Deleted
    def upsert(
        self,
        sql: str,  # pylint: disable=redefined-outer-name
        params: dict[str, Any] | None = None,
    ) -> None:
        """
        ## Args:
        - sql (str):
            SQL string.
        - params (dict, optional):
            If you need to embed a variable, make the embedded value and
            the variable a dictionary type.

        ## Example
        sql = "INSERT INTO hoge VALUES (%(fuga)s, %(piyo)s);"
        params = {'fuga': fuga, 'piyo': piyo}
        """
        warnings.warn(
            message="This method will be discontinued in the future.",
            category=FutureWarning,
        )
        with self._get_connection_old() as conn:  # pylint: disable=not-context-manager
            with conn.cursor() as cur:
                if params:
                    cur.execute(sql, params)
                else:
                    cur.execute(sql)
            conn.commit()

    async def _make_set(self, set_: Set) -> tuple[SQL, dict[str, Any]]:
        _key = str(hash(str(set_.value)))
        return (
            (sql.Identifier(set_.field) + SQL(" = ") + sql.Placeholder(_key)),
            {_key: set_.value},
        )

    async def _make_where(self, where: Where) -> tuple[SQL, dict[str, Any]]:
        _key = str(hash(str(where.value)))
        if where.operator == "in":
            return (
                sql.Identifier(where.field)
                + SQL(" = ANY(")
                + sql.Placeholder(_key)
                + SQL(")"),
                {_key: list(where.value)},
            )
        return (
            sql.Identifier(where.field)
            + SQL(f" {where.operator} ")
            + sql.Placeholder(_key),
            {_key: where.value},
        )

    async def _make_insert(
        self, set_: Set
    ) -> tuple[sql.Identifier, sql.Placeholder, dict[str, Any]]:
        _key = str(hash(str(set_.value)))
        return (
            sql.Identifier(set_.field),
            sql.Placeholder(_key),
            {_key: set_.value},
        )

    async def _make_sets(self, _data: Set | tuple[Set]) -> tuple[SQL, dict[str, Any]]:
        if isinstance(_data, Set):
            _sql, _param = await self._make_set(_data)
            return (_sql, _param)
        _sets: list[SQL] = []
        _params: list[dict] = []
        results = await asyncio.gather(*[self._make_set(set_) for set_ in _data])
        for _set, _param in results:
            _sets.append(_set)
            _params.append(_param)
        return (SQL(" ").join(seq=_sets), dict(ChainMap(*_params)))

    async def _make_wheres(
        self, _data: Where | tuple[Where], _join: str
    ) -> tuple[SQL, dict[str, Any]]:
        if isinstance(_data, Where):
            _sql, _param = await self._make_where(_data)
            return (SQL("WHERE ") + _sql, _param)
        _wheres: list[SQL] = []
        _params: list[dict] = []
        results = await asyncio.gather(*[self._make_where(where) for where in _data])
        for _where, _param in results:
            _wheres.append(_where)
            _params.append(_param)
        return (
            SQL("WHERE ") + SQL(f" {_join} ").join(seq=_wheres),
            dict(ChainMap(*_params)),
        )

    async def _make_inserts(
        self, _data: Set | tuple[Set]
    ) -> tuple[SQL, SQL, dict[str, Any]]:
        if isinstance(_data, Set):
            _field, _placeholder, _param = await self._make_insert(_data)
            return (_field, _placeholder, _param)
        _fields: list[sql.Identifier] = []
        _placeholders: list[sql.Placeholder] = []
        _params: list[dict] = []
        results = await asyncio.gather(*[self._make_insert(set_) for set_ in _data])
        for _field, _placeholder, _param in results:
            _fields.append(_field)
            _placeholders.append(_placeholder)
            _params.append(_param)
        return (
            SQL(", ").join(seq=_fields),
            SQL(", ").join(seq=_placeholders),
            dict(ChainMap(*_params)),
        )

    async def _make_sub_insert_sql(
        self, _data: MakeINSERT
    ) -> tuple[SQL, dict[str, Any] | None]:
        query: str = "INSERT INTO {table} ({fields}) VALUES ({values})"
        _fields, _placeholders, params = await self._make_inserts(_data.sets)
        return (
            SQL(obj=f"{query};").format(
                table=sql.Identifier(_data.table),
                fields=_fields,
                values=_placeholders,
            ),
            params,
        )

    async def _make_sub_select_sql(
        self, _data: MakeSELECT
    ) -> tuple[SQL, dict[str, Any] | None]:
        query: str = "SELECT {fields} FROM {table} {WHERES}"
        if isinstance(_data.fields, tuple):
            _fields = sql.SQL(", ").join(sql.Identifier(_f) for _f in _data.fields)
        else:
            _fields = sql.SQL(_data.fields)
        if _data.table in SP_ALLOW_TABLES:
            query: str = "SELECT {fields} FROM " + _data.table + " {WHERES}"
        if _data.wheres is None:
            query = re.sub(r"{WHERES}", "", query)
            return (
                SQL(obj=f"{query};").format(
                    fields=_fields,
                    table=sql.Identifier(_data.table),
                ),
                None,
            )
        _sql, _params = await self._make_wheres(_data.wheres, _data.join)
        return (
            SQL(obj=f"{query};").format(
                fields=_fields,
                table=sql.Identifier(_data.table),
                WHERES=_sql,
            ),
            _params,
        )

    async def _make_sub_update_sql(
        self, _data: MakeUPDATE
    ) -> tuple[SQL, dict[str, Any] | None]:
        query: str = "UPDATE {table} SET {SETS} {WHERES}"
        _sets_sql, _sets_params = await self._make_sets(_data.sets)
        if _data.wheres is None:
            query = re.sub(r"{WHERES}", "", query)
            return (
                SQL(obj=f"{query};").format(
                    table=sql.Identifier(_data.table),
                    SETS=_sets_sql,
                    WHERES="",
                ),
                _sets_params,
            )
        _wheres_sql, _wheres_params = await self._make_wheres(_data.wheres, _data.join)
        return (
            SQL(obj=f"{query};").format(
                table=sql.Identifier(_data.table),
                SETS=_sets_sql,
                WHERES=_wheres_sql,
            ),
            {**_sets_params, **_wheres_params},
        )

    async def _make_sub_delete_sql(
        self, _data: MakeDELETE
    ) -> tuple[SQL, dict[str, Any] | None]:
        query: str = "DELETE FROM {table} {WHERES}"
        if _data.wheres is None:
            query = re.sub(r"{WHERES}", "", query)
            return (
                SQL(obj=f"{query};").format(
                    table=sql.Identifier(_data.table), WHERES=""
                ),
                None,
            )
        _sql, _params = await self._make_wheres(_data.wheres, _data.join)
        return (
            SQL(obj=f"{query};").format(table=sql.Identifier(_data.table), WHERES=_sql),
            _params,
        )

    async def _make_sql(
        self, _data: MakeINSERT | MakeSELECT | MakeUPDATE | MakeDELETE
    ) -> tuple[SQL, dict[str, Any] | None]:
        _func = self._dict_make_sql_function.get(_data.__class__)
        if _func:
            return await _func(_data)
        # if isinstance(_data, MakeINSERT):
        #     return await self._make_sub_insert_sql(_data)
        # if isinstance(_data, MakeSELECT):
        #     return await self._make_sub_select_sql(_data)
        # if isinstance(_data, MakeUPDATE):
        #     return await self._make_sub_update_sql(_data)
        # if isinstance(_data, MakeDELETE):
        #     return await self._make_sub_delete_sql(_data)
        raise ArgsError(argument_name="_data")

    @overload
    async def execute(
        self, __query: MakeINSERT, __row_factory: Callable | None
    ) -> None: ...

    @overload
    async def execute(
        self, __query: MakeSELECT, __row_factory: Callable | None
    ) -> tuple | tuple[list[tuple], list[Column]]: ...

    @overload
    async def execute(
        self, __query: MakeUPDATE, __row_factory: Callable | None
    ) -> None: ...

    @overload
    async def execute(
        self, __query: MakeDELETE, __row_factory: Callable | None
    ) -> None: ...

    async def execute(
        self,
        __query: MakeINSERT | MakeSELECT | MakeUPDATE | MakeDELETE,
        __row_factory: Callable | None = None,
    ):
        """
        _summary_

        ### Args
        - query (MakeINSERT | MakeSELECT | MakeUPDATE | MakeDELETE):
            _description_

        ### Returns
        - tuple | list[tuple] | None:
            _description_
        """
        _sql, _params = await self._make_sql(__query)
        async with await self._get_connection() as conn:
            async with conn.cursor(row_factory=__row_factory) as cur:
                await cur.execute(query=_sql, params=_params)
                if isinstance(__query, MakeSELECT):
                    if __query.method == "fetchone":
                        return await cur.fetchone()
                    if __query.method == "fetchall":
                        return (await cur.fetchall(), cur.description)
                    raise ValueError("Passed undifined values.")
            await conn.commit()

    async def execute_many(
        self, __queries: tuple[MakeINSERT | MakeSELECT | MakeUPDATE | MakeDELETE]
    ) -> tuple[tuple | tuple[list[tuple], list[Column]] | None]:
        """
        _summary_

        ### Args
        - query (MakeINSERT | MakeSELECT | MakeUPDATE | MakeDELETE):
            _description_

        ### Returns
        - tuple | list[tuple] | None:
            _description_
        """
        _list: list[Task] = []
        async with asyncio.TaskGroup() as _tg:
            for _query in __queries:
                _list.append(_tg.create_task(self.execute(_query)))
        return tuple(_t.result() for _t in _list)

    def is_exists(
        self,
        table_name: str,
        params: _IsExstsParamsDictionary | list[_IsExstsParamsDictionary],
        join: Literal["AND", "OR"] | None = None,
    ) -> bool:
        """
        ## Args:
        - table_name (str):
            Name of the target table.
        - params (dict | list[dict]):
            List of dictionaries consisting of
            "target_column", "value", and "how"(optional).
            e.g.
            {
                target_column: str,
                values: Any | list[Any]
            )
        - join (Literal['AND', 'OR'] | None, optional):
            If multiple "params" arguments are specified,
            they must be set.
            The default value is None.

        ## Returns:
        - bool: Returns True if the value of the specified search condition
                exists in the table.
        """
        if isinstance(params, list):
            if not join and len(params) > 1:
                raise ArgsError(
                    argument_name="join",
                    add='To set multiple "params". "join" must be set.',
                )
        if re.search(r"\W", table_name):
            raise ArgsError(
                argument_name="table_name", add="Contains unauthorized charactes."
            )
        len_params: int = 0
        len_values: int = 0
        if isinstance(params, list):
            len_params = len(params)
            for param in params:
                if isinstance(param["values"], list):
                    len_values += len(param["values"])
                else:
                    len_values += 1
        else:
            len_params = 1
            if isinstance(params["values"], list):
                len_values += len(params["values"])
            else:
                len_values += 1
        random_string = NonDupulicateStringsGenerator(
            max_generation=len_params * len_values
        )
        _queries: list[str] = []
        query_params: dict[str, Any] = {}
        if isinstance(params, list):
            for _dict in params:
                _query: list[str] = []
                if isinstance(_dict["values"], list):
                    for value in _dict["values"]:
                        if re.search(r"\W", _dict["target_column"]):
                            raise ArgsError(
                                argument_name="params['target_column']",
                                add="Contains unauthorized charactes.",
                            )
                        __value_key = next(random_string)
                        _query.append(f"{_dict['target_column']} = %({__value_key})s")
                        query_params[__value_key] = value
                    if len(_dict["values"]) == 1:
                        _query_str = _query[0]
                    else:
                        _query_str = " OR ".join(_query)
                else:
                    if re.search(r"\W", _dict["target_column"]):
                        raise ArgsError(
                            argument_name="params['target_column']",
                            add="Contains unauthorized charactes.",
                        )
                    __value_key = next(random_string)
                    _query_str = f"{_dict['target_column']} = %({__value_key})s"
                    query_params[__value_key] = _dict["values"]
                _queries.append(_query_str)
            _queries_str = f" {join} ".join(_queries)
        elif isinstance(params, dict):
            _query: list[str] = []
            if isinstance(params["values"], list):
                for value in params["values"]:
                    if re.search(r"\W", params["target_column"]):
                        raise ArgsError(
                            argument_name="params['target_column']",
                            add="Contains unauthorized charactes.",
                        )
                    __value_key = next(random_string)
                    _query.append(f"{params['target_column']} = %({__value_key})s")
                    query_params[__value_key] = value
                if len(params["values"]) == 1:
                    _query_str = _query[0]
                else:
                    _query_str = " OR ".join(_query)
            else:
                if re.search(r"\W", params["target_column"]):
                    raise ArgsError(
                        argument_name="params['target_column']",
                        add="Contains unauthorized charactes.",
                    )
                __value_key = next(random_string)
                _query_str = f"{params['target_column']} = %({__value_key})s"
                query_params[__value_key] = params["values"]
            _queries_str = _query_str
        else:
            raise ArgsError(argument_name="params", add="Unsupported type.")
        _sql = f"SELECT EXISTS (SELECT * FROM {table_name} " f"WHERE {_queries_str});"
        res = self.select_fetchone(sql=_sql, params=query_params)
        if res is not None:
            return res[0]
        else:
            return False
