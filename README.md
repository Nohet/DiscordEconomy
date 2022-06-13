# DiscordEconomy 1.3.8
[![Downloads](https://pepy.tech/badge/discordeconomy)](https://pepy.tech/project/discordeconomy)
![PyPI - License](https://img.shields.io/pypi/l/DiscordEconomy)
[![Language grade: Python](https://img.shields.io/lgtm/grade/python/g/Nohet/DiscordEconomy.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/Nohet/DiscordEconomy/context:python)
[![Total alerts](https://img.shields.io/lgtm/alerts/g/Nohet/DiscordEconomy.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/Nohet/DiscordEconomy/alerts/)

Discord.py, other libs(hikari etc.), and forks(pycord, nextcord etc.) extension to create economy easily with support 
of **Sqlite**/**MongoDB**.

## Release Information
<details>
<summary>Release 1.3.8</summary>

- fixed typing for get_all_data function
</details>
<details>
<summary>Release 1.3.7</summary>

- added full typing for functions
</details>

<details>
<summary>Release 1.3.6</summary>

- deprecated DiscordEconomy.Economy(), use 'from DiscordEconomy.Sqlite import Economy' instead
- added support for mongodb
</details>

<details>
<summary>Release 1.3.5</summary>

- code rewrite
- add some more examples(including new discord.py slash commands, and adding a new minigame)
</details>

<details about="Release Information">

<summary>Release 1.3.4</summary>

- added checking for the latest version
- code rewrite
</details>

<details about="Release Information">

<summary>Release 1.3.3</summary>

- Added simple documentation
</details>




## Important Links
* [Documentation](https://nohet.github.io/DiscordEconomy/)

## Installation

You can install package directly from pypi

`pip install DiscordEconomy`
 
## Functions available

The current list of asynchronous functions available are:

```python
await <economy>.is_registered(user_id)
await <economy>.get_user(user_id)
await <economy>.delete_user_account(user_id)
await <economy>.get_all_data()
await <economy>.add_money(user_id, value, amount)
await <economy>.remove_money(user_id, value, amount)
await <economy>.set_money(user_id, value, amount)
await <economy>.add_item(user_id, item)
await <economy>.remove_item(user_id, item)
 ```
 

## Example Usage

**All the examples for this package are available on [GitHub](https://github.com/Nohet/DiscordEconomy/tree/main/examples)**

Note that for using this examples you have to change token to yours and:
- enable message and member intent in discord developer portal while using message commands example
- enable member intent in discord developer portal and pass guild id where to register slash commands while using slash commands example
