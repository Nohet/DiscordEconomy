import asyncio

from typing import Optional

from ..exceptions import (NoItemFound, ItemAlreadyExists)
from ..objects import UserObject

from ..__version__ import check_for_updates
from motor import motor_asyncio
from nest_asyncio import apply

apply()


class Economy:
    def __init__(self, mongo_url: str, database_name: str, collection: Optional[str] = "economy"):
        """
        Initialize connection with a database.
        """
        self.__client = motor_asyncio.AsyncIOMotorClient(mongo_url, serverSelectionTimeoutMS=5000)

        self.__db = self.__client[database_name]
        self.collection = self.__db[collection]

        asyncio.get_event_loop().run_until_complete(check_for_updates())


    async def is_registered(self, user_id):
        """
        **Params**:
        \n
        user_id - user id to check if it is in the database

        **Returns**:
        \n
        bool
        """

        user = await self.collection.find_one({"_id": user_id})
        if not user:
            user_obj = {"_id": user_id, "bank": 0, "wallet": 0, "items": []}

            await self.collection.insert_one(user_obj)

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

        r = await self.collection.find_one({"_id": user_id})

        return UserObject(r["bank"], r["wallet"], r["items"])

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

        await self.collection.delete_one({"_id": user_id})

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

        data = self.collection.find()

        async for user in data:
            yield UserObject(user["bank"], user["wallet"], user["items"])

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

        user = await self.collection.find_one({"_id": user_id})

        await self.collection.update_one({"_id": user_id}, {"$set": {value: user[value] + amount}})

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

        user = await self.collection.find_one({"_id": user_id})

        await self.collection.update_one({"_id": user_id}, {"$set": {value: user[value] - amount}})

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

        await self.collection.update_one({"_id": user_id}, {"$set": {value: amount}})

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

        r = await self.collection.find_one({"_id": user_id})

        if item in r["items"]:
            raise ItemAlreadyExists("User already have this item")

        r["items"].append(item)
        await self.collection.update_one({"_id": user_id}, {"$set": {"items": r["items"]}})


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

        r = await self.collection.find_one({"_id": user_id})

        if item in r["items"]:
            r["items"].pop(r["items"].index(item))

            await self.collection.update_one({"_id": user_id}, {"$set": {"items": r["items"]}})

            return True

        else:
            raise NoItemFound("User doesn't have this item")
