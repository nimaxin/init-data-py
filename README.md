# init-data-py

![Package version](https://img.shields.io/pypi/v/init-data-py?color=%2334D058&label=pypi%20package)
![License](https://img.shields.io/github/license/nimaxin/init-data-py)

A Python library that provides tools for using and validating Telegram web app init data.

## Installation

You can install the library using pip:

```bash
pip install init-data-py
```

## Usage

### Parsing

To parse the `window.Telegram.WebApp.initData` query string into an `InitData` object for easier access to attributes and validation, you can use the `InitData.parse` method:

```python
from init_data_py import InitData

init_data = InitData.parse(query_string)
```

### Validation

To validate the init data, you can use the `InitData.validate` method:

```python
is_valid = init_data.validate(bot_token)
```

### Signing

If you need to create and sign your own init data, you can create an `InitData` object and sign it:

```python
from init_data_py import InitData
from init_data_py.types import User

user = User(id=5167898484, first_name="xin")
init_data = InitData(user=user).sign(bot_token)
```

### Converting InitData to Query String

After creating and signing init data, you can convert it to a query sting using the `InitData.to_query_string` method:

```python
query_string = init_date.to_query_string()
```

### Real-World Validation Example

This example demonstrates how to validate a Telegram Mini App init data. It parses the init data query string into an `InitData` object and validate it using the provided bot token, checking that the data is valid and has not expired:

```python
from init_data_py import InitData

bot_token = "7244657541:AAEgqk0HDC3WD5cdbnGMdd6L0TJ74FDp97Y"
query_string = "query_id=AAF03wc0AgAAAHTfBzROOCVW&user=%7B%22id%22%3A5167898484%2C%22first_name%22%3A%22xin%22%2C%22last_name%22%3A%22%22%2C%22username%22%3A%22pvnimaxin%22%2C%22language_code%22%3A%22en%22%2C%22allows_write_to_pm%22%3Atrue%7D&auth_date=1722938610&hash=8654c8c617c143abf656f4f159be2539880a56f58c2d9be622f90c0346aa162b"

init_data = InitData.parse(query_string)

is_valid = init_data.validate(
    bot_token=bot_token,
    lifetime=3600,
)
```

## License

This library is licensed under the [MIT License](LICENCE).
