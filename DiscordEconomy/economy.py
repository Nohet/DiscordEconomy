import asyncio
import aiosqlite

from typing import Optional

from .exceptions import (NoItemFound, ItemAlreadyExists)
from .objects import UserObject

from .__version__ import check_for_updates


class Economy:
    def __init__(self, database_name: Optional[str] = "database.db"):
        """
        Initialize default options, save database name
        """

        self.__database_name = database_name
        self.__loop = asyncio.get_event_loop()

        self.__loop.run_until_complete(self.__is_table_exists())
        self.__loop.run_until_complete(check_for_updates())


    async def __is_table_exists(self):
        """Checks if table exists, if not it creates economy table"""

        con = await aiosqlite.connect(self.__database_name)
        c = await con.cursor()

        await c.execute("CREATE TABLE IF NOT EXISTS economy(id integer, bank integer, wallet integer, items text)")

        await con.commit()
        await con.close()

    async def is_registered(self, user_id):
        """
        **Params**:
        \n
        user_id - user id to check if it is in the database

        **Returns**:
        \n
        bool
        """

        con = await aiosqlite.connect(self.__database_name)
        c = await con.cursor()

        query = await c.execute("SELECT * FROM economy WHERE id = ?", (user_id,))
        query = await query.fetchone()

        if not query:
            await c.execute(f"INSERT INTO economy VALUES(?, 0, 0, ?)", (user_id, ""))

        await con.commit()
        await con.close()

        return True

    async def get_user(self, user_id):
        """
        Obtains user from a database

        **Code Example**:
        \n
        ```python
        import DiscordEconomy
        import asyncio

        economy = DiscordEconomy.Economy()


        async def main() -> None:
            await economy.is_registered(12345)
            user = await economy.get_user(12345)

            print(user.wallet)
            print(user.bank)
            print(user.items)

        asyncio.get_event_loop().run_until_complete(main())
        ```

        **Params**:
        \n
        user_id - user id to obtain it from this id

        **Returns**:
        \n
        UserObject

        """

        con = await aiosqlite.connect(self.__database_name)
        c = await con.cursor()

        r = await c.execute("SELECT * FROM economy WHERE id = ?", (user_id,))
        r = await r.fetchone()

        await con.close()

        bank = r[1]
        wallet = r[2]
        items = r[3].split(" | ")

        if items[0] == "":
            items.pop(0)

        return UserObject(bank, wallet, items)

    async def delete_user_account(self, user_id):
        """
        Deletes user account from a database

        **Params**:
        \n
        user_id - which user should be deleted

        **Returns**:
        \n
        bool
        """

        con = await aiosqlite.connect(self.__database_name)
        c = await con.cursor()

        await c.execute("DELETE FROM economy WHERE id = ?", (user_id,))

        await con.commit()
        await con.close()

        return True

    async def get_all_data(self):
        """
        Obtains all data from database

        **Code Example**:
        \n
        ```python
        import DiscordEconomy
        import asyncio

        economy = DiscordEconomy.Economy()


        async def main() -> None:
            r = economy.get_all_data()
            async for i in r:
                print(i.bank)

        asyncio.get_event_loop().run_until_complete(main())
        ```

        **Params**:
        \n
        Doesn't take any params

        **Returns**:
        \n
        async generator of UserObject

        """

        con = await aiosqlite.connect(self.__database_name)
        c = await con.cursor()

        r = await c.execute("SELECT * FROM economy")
        r = await r.fetchall()

        await con.close()

        for user in r:
            items = user[3].split(" | ")

            if items[0] == "":
                items.pop(0)

            yield UserObject(user[1], user[2], items)

    async def add_money(self, user_id, value, amount):
        """
        Adds money to user account

        **Code Example**:
        \n
        ```python
        import DiscordEconomy
        import asyncio

        economy = DiscordEconomy.Economy()


        async def main() -> None:
            await economy.is_registered(12345)
            await economy.add_money(12345, "wallet", 500)

        asyncio.get_event_loop().run_until_complete(main())
        ```

        **Params**:
        \n
        user_id - user id to add money to

        value - in what place money should be added, for example 'bank' or 'wallet'

        amount - how much should be added to user account

        **Returns**:
        \n
        bool
        """

        con = await aiosqlite.connect(self.__database_name)
        c = await con.cursor()

        user_account = await c.execute(f"SELECT {value} FROM economy WHERE id = ?", (user_id,))
        user_account = await user_account.fetchone()
        user_account = user_account[0]

        money = user_account + amount

        await c.execute(f"UPDATE economy SET {value} = ? WHERE id = ?", (money, user_id,))

        await con.commit()
        await con.close()

        return True

    async def remove_money(self, user_id, value, amount):
        """
        Adds money to user account

        **Params**:
        \n
        user_id - user id to add money to

        value - in what place money should be removed, for example 'bank' or 'wallet'

        amount - how much should be removed from user account

        **Returns**:
        \n
        bool
        """

        con = await aiosqlite.connect(self.__database_name)
        c = await con.cursor()

        user_account = await c.execute(f"SELECT {value} FROM economy WHERE id = ?", (user_id,))
        user_account = await user_account.fetchone()
        user_account = user_account[0]

        money = user_account - amount

        await c.execute(f"UPDATE economy SET {value} = ? WHERE id = ?", (money, user_id,))

        await con.commit()
        await con.close()

        return True

    async def set_money(self, user_id, value, amount):
        """
        Sets user money to certain amount

        **Params**:
        \n
        user_id - user id to set money

        value - in what place money should be set, for example 'bank' or 'wallet'

        amount - to what amount money should be set

        **Returns**:
        \n
        bool
        """

        con = await aiosqlite.connect(self.__database_name)
        c = await con.cursor()

        await c.execute(f"UPDATE economy SET {value} = ? WHERE id = ?", (amount, user_id,))

        await con.commit()
        await con.close()

        return True

    async def add_item(self, user_id, item):
        """
        Adds item to user account

        **Code Example**:
        \n
        ```python
        import DiscordEconomy
        import asyncio

        economy = DiscordEconomy.Economy()


        async def main() -> None:
            await economy.is_registered(12345)
            await economy.add_item(12345, "sword")

        asyncio.get_event_loop().run_until_complete(main())
        ```

        **Params**:
        \n
        user_id - user id where the item should be added

        item - which item should be added to user

        **Returns**:
        \n
        bool | if user already have this item raises ItemAlreadyExists
        """

        con = await aiosqlite.connect(self.__database_name)
        c = await con.cursor()

        query = await c.execute("SELECT items FROM economy WHERE id = ?", (user_id,))
        query = await query.fetchone()

        _user_items = query[0].split(" | ")

        if item in _user_items:
            raise ItemAlreadyExists("User already have this item")

        _user_items.append(item)

        await c.execute("UPDATE economy SET items = ? WHERE id = ?", (" | ".join(_user_items), user_id))

        await con.commit()
        await con.close()

        return True

    async def remove_item(self, user_id, item):
        """
        Removes item to user account

        **Params**:
        \n
        user_id - user id where the item should be removed

        item - which item should be removed from user

        **Returns**:
        \n
        bool | if user doesn't have this item
        """

        con = await aiosqlite.connect(self.__database_name)
        c = await con.cursor()

        query = await c.execute("SELECT items FROM economy WHERE id = ?", (user_id,))
        query = await query.fetchone()

        _user_items = query[0].split(" | ")

        if item in _user_items:
            _user_items.pop(_user_items.index(item))

            await c.execute("UPDATE economy SET items = ? WHERE id = ?", (" | ".join(_user_items), user_id))

            await con.commit()
            await con.close()

            return True

        else:
            raise NoItemFound("User doesn't have this item")
