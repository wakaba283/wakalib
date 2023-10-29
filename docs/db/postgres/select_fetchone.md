## select_fetchone
#### Args
- sql (str)  
    Any SQL. select statement.

- params (dict, optional)  
    If you need to embed a variable, make the embedded value and
    the variable a dictionary type.

## Returns:
- tuple: Search results are returned as a tuple.

## Example
```python
my_db = DBHandling(
    credential_filepath='credential.json',
    role='fuga_role'
)

sql = "SELECT my_column FROM my_table WHERE my_column=%(ANY_KEY)s;"
params = {'ANY_KEY': 'VALUE'}

results = my_db.select_fetchone(
    sql=sql,
    params=params
)

print(results)
# ('my_value',)
```
