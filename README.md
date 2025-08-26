# DiscordEconomy 2.0.0

[![Downloads](https://pepy.tech/badge/discordeconomy)](https://pepy.tech/project/discordeconomy)
![PyPI - License](https://img.shields.io/pypi/l/DiscordEconomy)
[![CodeFactor](https://www.codefactor.io/repository/github/nohet/discordeconomy/badge)](https://www.codefactor.io/repository/github/nohet/discordeconomy)

A modern and flexible **economy system extension** for Discord bots.
Supports **discord.py**, **hikari**, and forks like **pycord** or **nextcord**.
Database support: **SQLite** and **MongoDB**.

---

## ✨ Features

* Plug-and-play economy system for Discord bots
* Full async support
* SQLite & MongoDB backends
* Easy integration with commands, slash commands, or custom handlers
* Type hints for better DX (developer experience)
* Ready-to-use examples

---

## 📦 Installation

Install directly from PyPI:

```bash
pip install DiscordEconomy
```

---

## 🚀 Quick Start

```python
from DiscordEconomy.Sqlite import Economy

economy = Economy("economy.db")
user_id = 12345

# Register user
await economy.ensure_registered(user_id)

# Add money
await economy.add_money(user_id, "wallet", 500)

# Get user info
user = await economy.get_user(user_id)
print(user)
```

More examples are available in the [examples folder](https://github.com/Nohet/DiscordEconomy/tree/main/examples).

---

## ⚙️ API Overview

Available async functions:

```python
await economy.ensure_registered(user_id)
await economy.get_user(user_id)
await economy.delete_user_account(user_id)
await economy.get_all_users()
await economy.add_money(user_id, field, amount)
await economy.remove_money(user_id, field, amount)
await economy.set_money(user_id, field, amount)
await economy.add_item(user_id, item)
await economy.remove_item(user_id, item)
```

---

## 📜 Release Notes

<details>
<summary><b>2.0.0</b></summary>
- Complete rewrite (not backward compatible)  
</details>

<details>
<summary><b>1.3.8</b></summary>
- Fixed typing for `get_all_data`  
</details>

<details>
<summary><b>1.3.7</b></summary>
- Full typing for functions  
</details>

<details>
<summary><b>1.3.6</b></summary>
- Deprecated `DiscordEconomy.Economy()`, use `from DiscordEconomy.Sqlite import Economy`  
- Added MongoDB support  
</details>

<details>
<summary><b>1.3.5</b></summary>
- Code rewrite  
- More examples (slash commands + new minigame)  
</details>

<details>
<summary><b>1.3.4</b></summary>
- Added version checker  
- Code rewrite  
</details>

<details>
<summary><b>1.3.3</b></summary>
- Added simple documentation  
</details>

---

## 🔑 Notes

* Replace the bot token in examples with your own.
* Enable **Message Intent** and **Member Intent** in the Discord Developer Portal if you use message commands.
* For slash commands, enable **Member Intent** and provide your Guild ID.
