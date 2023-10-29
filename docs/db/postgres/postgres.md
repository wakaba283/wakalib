# Documentation for postgres module
You can check the operation about DB in PostgreSQL.

\* Postgres and PostgreSQL are all registered trademarks of
the PostgreSQL Community Association of Canada.

## Introduction
To begin, you will need to prepare a JSON file with the following configuration for use with this module.

```json
{
    "KEY"*:{
        "name": "YOUR_DATABASE_NAME",
        "user": "ROLE_or_USER_NAME_TO_BE_USED",
        "password": "ROLE_or_USER_PASSWORD_TO_BE_USED",
        "host": "YOUR_DATABASE_HOST",
        "port": "YOUR_DATABASE_PORT"
    },
    ...
}
```
\* KEY naming is optional. I believe that describing it in the form of "DATABASE NAME / ROLEorUSER_NAME_TO_BE_USED" improves readability. (e.g.) my_db/my_role


## DBHandling
```python
DBHandling(credential_filepath: str, role: str)
```
This is the main class of this module.  
It is instantiated by passing the following arguments.

#### Args
- credentials_filepath (str)  
    Path to the JSON file created above.

- role (str)  
    The KEY you defined in the JSON you created above.

#### Attribute
- role (str)  
KEY passed when instantiated.

- _db_config (dict)  
Converts JSON passed at instantiation into dict and returns it.

#### Example
```python
my_db = DBHandling(
    credential_filepath='credential.json',
    role='my_role'
)

print(my_db.role)
# 'my_role'
```

## Methods
```{toctree}
:maxdepth: 2
:caption: Contents:
select_fetchone
```