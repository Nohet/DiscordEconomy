import asyncio
import typing

from ..constants import VALID_FIELDS_LITERAL, VALID_FIELDS
from ..exceptions import (
    NotFoundException,
    ItemAlreadyExists,
    NegativeAmountException,
    EnsurePositiveBalanceException,
)
from ..objects import User, Item
from ..__version__ import check_for_updates
from motor import motor_asyncio

__all__ = ["Economy"]


class Economy:
    """
    An asynchronous MongoDB-based economy system for managing user balances and items.

    This class provides methods to manage user accounts, currency balances, and inventory items
    using MongoDB with optimized connection handling.

    Attributes:
        mongo_url (str): MongoDB connection URL
        database_name (str): Name of the MongoDB database
        collection (str): Name of the collection to store user data
        ensure_positive_balance (bool): If True, prevents balances from going negative
                                        through validation checks
    """

    def __init__(
        self,
        mongo_url: str,
        database_name: str,
        collection: typing.Optional[str] = "economy",
        ensure_positive_balance: bool = True,
    ):
        """
        Initialize the economy system with MongoDB connection settings.

        Args:
            mongo_url: MongoDB connection URL
            database_name: Name of the MongoDB database
            collection: Name of the collection to store user data.
                       Defaults to "economy"
            ensure_positive_balance: Whether to prevent negative balances.
                                    Defaults to True

        Note:
            Automatically checks for package updates during initialization.
        """
        self.__ensure_positive_balance = ensure_positive_balance
        self.__client = motor_asyncio.AsyncIOMotorClient(
            mongo_url, serverSelectionTimeoutMS=5000
        )

        self.__db = self.__client[database_name]
        self.__collection = self.__db[collection]

        try:
            self.__loop = asyncio.get_running_loop()
        except RuntimeError:
            self.__loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.__loop)

        self.__loop.run_until_complete(check_for_updates())

    async def ensure_registered(self, user_id: typing.Union[str, int]) -> None:
        """
        Check if a user exists in the database, registering them if not found.

        Args:
            user_id: Discord user ID or unique identifier

        Example:
            >> await economy.ensure_registered(1234567890)
        """
        user = await self.__collection.find_one({"_id": user_id})
        if not user:
            user_obj = {"_id": user_id, "bank": 0, "wallet": 0, "items": []}
            await self.__collection.insert_one(user_obj)

    async def get_user(self, user_id: typing.Union[str, int]) -> User:
        """
        Retrieve a user's complete economic profile including items.

        Args:
            user_id: Discord user ID or unique identifier

        Returns:
            User: User object containing balance information and items

        Raises:
            NoItemFoundException: If the specified user doesn't exist

        Example:
            >> user = await economy.get_user(1234567890)
            >> print(user.bank, user.wallet, user.items)
        """
        r = await self.__collection.find_one({"_id": user_id})

        if not r:
            raise NotFoundException(f"User {user_id} not found")

        # Convert item strings to Item objects
        items = [
            Item(idx, item_name, user_id) for idx, item_name in enumerate(r["items"])
        ]

        return User(user_id, r["bank"], r["wallet"], items)

    async def delete_user_account(self, user_id: typing.Union[str, int]) -> None:
        """
        Permanently delete a user account and all associated items.

        Args:
            user_id: Discord user ID or unique identifier

        Note:
            This action is irreversible and will remove all user data including items.
        """
        await self.__collection.delete_one({"_id": user_id})

    async def get_all_users(self) -> typing.AsyncGenerator[User, None]:
        """
        Retrieve all users from the database as an asynchronous generator.

        Yields:
            User: Complete user objects with balances and items

        Example:
            >> async for user in economy.get_all_users():
            ...     print(f"User {user.id}: {user.bank} coins")
        """
        data = self.__collection.find()

        async for user in data:
            # Convert item strings to Item objects
            items = [
                Item(idx, item_name, user["_id"])
                for idx, item_name in enumerate(user["items"])
            ]
            yield User(user["_id"], user["bank"], user["wallet"], items)

    async def add_money(
        self,
        user_id: typing.Union[str, int],
        field: VALID_FIELDS_LITERAL,
        amount: typing.Union[float, int],
    ) -> None:
        """
        Add money to a user's specified balance field.

        Args:
            user_id: Discord user ID or unique identifier
            field: Balance field to modify ('bank' or 'wallet')
            amount: Positive amount to add

        Raises:
            ValueError: If invalid field specified
            NegativeAmountException: If negative amount provided
            NoItemFoundException: If user doesn't exist

        Example:
            >> await economy.add_money(1234567890, "wallet", 100)
        """
        if amount < 0:
            raise NegativeAmountException(
                "Invalid amount. Amount cannot be less than 0"
            )

        if field not in VALID_FIELDS:
            raise ValueError(
                f"Invalid field: {field}. Must be one of: {', '.join(VALID_FIELDS)}"
            )

        await self.ensure_registered(user_id)

        user = await self.__collection.find_one({"_id": user_id})
        await self.__collection.update_one(
            {"_id": user_id}, {"$set": {field: user[field] + amount}}
        )

    async def remove_money(
        self,
        user_id: typing.Union[str, int],
        field: VALID_FIELDS_LITERAL,
        amount: typing.Union[float, int],
    ) -> None:
        """
        Remove money from a user's specified balance field.

        Args:
            user_id: Discord user ID or unique identifier
            field: Balance field to modify ('bank' or 'wallet')
            amount: Positive amount to remove

        Raises:
            ValueError: If invalid field specified
            NegativeAmountException: If negative amount provided
            NoItemFoundException: If user doesn't exist

        Example:
            >> await economy.remove_money(1234567890, "bank", 50)
        """
        if amount < 0:
            raise NegativeAmountException(
                "Invalid amount. Amount cannot be less than 0"
            )

        if field not in VALID_FIELDS:
            raise ValueError(
                f"Invalid field: {field}. Must be one of: {', '.join(VALID_FIELDS)}"
            )

        await self.ensure_registered(user_id)

        user = await self.__collection.find_one({"_id": user_id})

        if self.__ensure_positive_balance:
            balance = user[field]
            if balance - amount < 0:
                await self.set_money(user_id, field, 0)
                return

        await self.__collection.update_one(
            {"_id": user_id}, {"$set": {field: user[field] - amount}}
        )

    async def set_money(
        self,
        user_id: typing.Union[str, int],
        field: VALID_FIELDS_LITERAL,
        amount: typing.Union[float, int],
    ) -> None:
        """
        Set a user's balance field to a specific amount.

        Args:
            user_id: Discord user ID or unique identifier
            field: Balance field to modify ('bank' or 'wallet')
            amount: New absolute value for the balance

        Raises:
            ValueError: If invalid field specified
            EnsurePositiveBalanceException: If trying to set negative balance when ensure_positive_balance is True
            NoItemFoundException: If user doesn't exist

        Example:
            >> await economy.set_money(1234567890, "wallet", 200)
        """
        if self.__ensure_positive_balance and amount < 0:
            raise EnsurePositiveBalanceException(
                "Ensure positive balance is turned on."
                " User's balance cannot be set to less than 0."
            )

        if field not in VALID_FIELDS:
            raise ValueError(
                f"Invalid field: {field}. Must be one of: {', '.join(VALID_FIELDS)}"
            )

        await self.ensure_registered(user_id)

        await self.__collection.update_one({"_id": user_id}, {"$set": {field: amount}})

    async def add_item(self, user_id: typing.Union[str, int], item_name: str) -> None:
        """
        Add an item to a user's inventory.

        Args:
            user_id: Discord user ID or unique identifier
            item_name: Name of the item to add

        Raises:
            ItemAlreadyExists: If user already possesses this item
            NoItemFoundException: If user doesn't exist

        Example:
            >> await economy.add_item(1234567890, "magic_sword")
        """
        await self.ensure_registered(user_id)

        r = await self.__collection.find_one({"_id": user_id})

        if item_name in r["items"]:
            raise ItemAlreadyExists("User already have this item")

        r["items"].append(item_name)
        await self.__collection.update_one(
            {"_id": user_id}, {"$set": {"items": r["items"]}}
        )

    async def remove_item(
        self, user_id: typing.Union[str, int], item_name: str
    ) -> None:
        """
        Remove an item from a user's inventory.

        Args:
            user_id: Discord user ID or unique identifier
            item_name: Name of the item to remove

        Raises:
            NoItemFoundException: If either user doesn't exist or item not found

        Example:
            >> await economy.remove_item(1234567890, "old_sword")
        """
        await self.ensure_registered(user_id)

        r = await self.__collection.find_one({"_id": user_id})

        if item_name in r["items"]:
            r["items"].pop(r["items"].index(item_name))

            await self.__collection.update_one(
                {"_id": user_id}, {"$set": {"items": r["items"]}}
            )
        else:
            raise NotFoundException(f"Item {item_name} not found for user {user_id}")
