# init-data-py

![Package version](https://img.shields.io/pypi/v/init-data-py?color=%2334D058&label=pypi%20package)
![License](https://img.shields.io/github/license/nimaxin/init-data-py)

A Python library that provides tools for using and validating Telegram web app init data.

---

## Installation

You can install the library using pip.

```bash
pip install init-data-py
```

## Usage

### Parsing.

```python
from init_data_py import InitData

query_string = "query_id=AAF03wc0Ag..."

InitData.from_query_string(query_string)
```

### Signing

```python
from init_data_py import InitData
from init_data_py.types import User

BOT_TOKEN = "7244657541:AA..."

init_data = InitData(
    user=User(
        id=5167898484,
        first_name="xin",
        username="pvnimaxin",
    )
).sign(bot_token=BOT_TOKEN)
```

### Validation

```python
from init_data_py import InitData

BOT_TOKEN = "7244657541:AA..."

init_data = InitData(...)
is_valid = init_data.validate(bot_token=BOT_TOKEN, lifetime=3600)
```

## License

This library is licensed under the [MIT License](LICENCE).
