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

import json
import re
from typing import Any, Literal, TypedDict

import pandas as pd
import psycopg2

from wakalib.exceptions.exception import ArgsError
from wakalib.py.generic import NonDupulicateStringsGenerator


class _IsExstsParamsDictionary(TypedDict):
    target_column: str
    values: Any | list[Any]


class DBHandling:
    """
    Set up and manipulate database credentials.
    """
    def __init__(
            self,
            credentials_filepath: str,
            role: str
        ) -> None:
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
        self.__role = role
        with open(
            file=credentials_filepath, mode='rt', encoding='utf-8'
        ) as _file:
            credentials = json.load(_file)
        if not credentials.get(role):
            raise ValueError(
                'The specified role name is not found in the credentials file.'
            )
        self.__db_config = credentials[role]

    @property
    def role(self):  # pylint: disable=missing-function-docstring
        return self.__role

    @property
    def _db_config(self):  # pylint: disable=missing-function-docstring
        return self.__db_config

    def _get_connection(self):
        return psycopg2.connect(
            dbname=self._db_config['name'],
            user=self._db_config['user'],
            password=self._db_config['password'],
            host=self._db_config['host'],
            port=self._db_config['port']
        )

    def select_fetchone(
            self, sql: str,
            params: dict[str, Any] | None = None
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
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                if params:
                    cur.execute(sql, params)
                else:
                    cur.execute(sql)
                data = cur.fetchone()
        return data

    def select_fetchall(
            self, sql: str,
            params: dict[str, Any] | None = None
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
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                if params:
                    cur.execute(sql, params)
                else:
                    cur.execute(sql)
                data = pd.DataFrame(
                    cur.fetchall(),
                    columns=[col.name for col in cur.description]
                    )
        return data

    def upsert(
            self, sql: str,
            params: dict[str, Any] | None = None
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
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                if params:
                    cur.execute(sql, params)
                else:
                    cur.execute(sql)
            conn.commit()

    def is_exists(
            self,
            table_name: str,
            params: _IsExstsParamsDictionary | list[_IsExstsParamsDictionary],
            join: Literal['AND', 'OR'] | None = None
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
                    argument_name='join',
                    add='To set multiple "params". "join" must be set.'
                )
        if re.search(r'\W', table_name):
            raise ArgsError(
                argument_name='table_name',
                add='Contains unauthorized charactes.'
            )
        len_params: int = 0
        len_values: int = 0
        if isinstance(params, list):
            len_params = len(params)
            for param in params:
                if isinstance(param['values'], list):
                    len_values += len(param['values'])
                else:
                    len_values += 1
        else:
            len_params = 1
            if isinstance(params['values'], list):
                len_values += len(params['values'])
            else:
                len_values += 1
        random_string = NonDupulicateStringsGenerator(
            max_generation=len_params*len_values
        )
        _queries: list[str] = []
        query_params: dict[str, Any] = {}
        if isinstance(params, list):
            for _dict in params:
                _query: list[str] = []
                if isinstance(_dict['values'], list):
                    for value in _dict['values']:
                        if re.search(r'\W', _dict['target_column']):
                            raise ArgsError(
                                argument_name="params['target_column']",
                                add='Contains unauthorized charactes.'
                            )
                        __value_key = next(random_string)
                        _query.append(
                            f"{_dict['target_column']} = %({__value_key})s"
                        )
                        query_params[__value_key] = value
                    if len(_dict['values']) == 1:
                        _query_str = _query[0]
                    else:
                        _query_str = ' OR '.join(_query)
                else:
                    if re.search(r'\W', _dict['target_column']):
                        raise ArgsError(
                            argument_name="params['target_column']",
                            add='Contains unauthorized charactes.'
                        )
                    __value_key = next(random_string)
                    _query_str = \
                        f"{_dict['target_column']} = %({__value_key})s"
                    query_params[__value_key] = _dict['values']
                _queries.append(_query_str)
            _queries_str = f' {join} '.join(_queries)
        elif isinstance(params, dict):
            _query: list[str] = []
            if isinstance(params['values'], list):
                for value in params['values']:
                    if re.search(r'\W', params['target_column']):
                        raise ArgsError(
                            argument_name="params['target_column']",
                            add='Contains unauthorized charactes.'
                        )
                    __value_key = next(random_string)
                    _query.append(
                        f"{params['target_column']} = %({__value_key})s"
                    )
                    query_params[__value_key] = value
                if len(params['values']) == 1:
                    _query_str = _query[0]
                else:
                    _query_str = ' OR '.join(_query)
            else:
                if re.search(r'\W', params['target_column']):
                    raise ArgsError(
                        argument_name="params['target_column']",
                        add='Contains unauthorized charactes.'
                    )
                __value_key = next(random_string)
                _query_str = \
                    f"{params['target_column']} = %({__value_key})s"
                query_params[__value_key] = params['values']
            _queries_str = _query_str
        else:
            raise ArgsError(
                argument_name='params',
                add='Unsupported type.'
            )
        _sql = (
            f"SELECT EXISTS (SELECT * FROM {table_name} "
            f"WHERE {_queries_str});"
        )
        res = self.select_fetchone(sql=_sql, params=query_params)
        if res is not None:
            return res[0]
        else:
            return False
