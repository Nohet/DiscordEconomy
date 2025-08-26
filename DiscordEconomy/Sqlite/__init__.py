import asyncio
import typing
import aiosqlite

from aiosqlitepool import SQLiteConnectionPool

from ..constants import VALID_FIELDS, VALID_FIELDS_LITERAL
from ..exceptions import (
    NotFoundException,
    NegativeAmountException,
    EnsurePositiveBalanceException,
)
from ..objects import User, Item
from ..__version__ import check_for_updates

__all__ = ["Economy"]


class Economy:
    """
    An asynchronous SQLite-based economy system for managing user balances and items.

    This class provides methods to manage user accounts, currency balances, and inventory items
    using SQLite with connection pooling for efficient database operations.

    Attributes:
        database_name (str): The name/path of the SQLite database file
        ensure_positive_balance (bool): If True, prevents balances from going negative
                                        through validation checks
    """

    def __init__(
        self,
        database_name: typing.Optional[str] = "economy.db",
        ensure_positive_balance: bool = True,
    ):
        """
        Initialize the economy system with database connection settings.

        Args:
            database_name: Name/path of the SQLite database file.
                         Defaults to "economy.db"
            ensure_positive_balance: Whether to prevent negative balances.
                                    Defaults to True

        Note:
            Automatically checks for table existence and creates them if needed.
            Also checks for package updates during initialization.
        """
        self.__ensure_positive_balance = ensure_positive_balance
        self.__database_name = database_name

        try:
            self.__loop = asyncio.get_running_loop()
        except RuntimeError:
            self.__loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.__loop)

        self.pool = SQLiteConnectionPool(self.__connection_factory)

        self.__loop.run_until_complete(self.__is_table_exists())
        self.__loop.run_until_complete(check_for_updates())

    async def __connection_factory(self) -> aiosqlite.Connection:
        """
        Create and configure a new database connection.

        Returns:
            aiosqlite.Connection: Configured database connection with optimized settings

        Note:
            Applies performance optimizations including WAL journal mode,
            normalized synchronization, and increased cache size.
        """
        conn = await aiosqlite.connect(self.__database_name)

        # Performance optimization settings
        await conn.execute("PRAGMA journal_mode = WAL")
        await conn.execute("PRAGMA synchronous = NORMAL")
        await conn.execute("PRAGMA cache_size = 10000")
        await conn.execute("PRAGMA temp_store = MEMORY")
        await conn.execute("PRAGMA foreign_keys = ON")
        await conn.execute("PRAGMA mmap_size = 268435456")

        return conn

    async def __is_table_exists(self) -> None:
        """
        Ensure required database tables exist, creating them if necessary.

        Creates:
        - users table with id (primary key), bank, and wallet columns
        - items table with id, itemName, ownerID columns and foreign key constraint
        - Index on ownerID for faster item queries
        """
        async with self.pool.connection() as conn:
            await conn.execute(
                """CREATE TABLE IF NOT EXISTS users
                   (
                       id     INTEGER PRIMARY KEY,
                       bank   NUMERIC,
                       wallet NUMERIC
                   )"""
            )
            await conn.execute(
                """CREATE TABLE IF NOT EXISTS items
                   (
                       id       INTEGER PRIMARY KEY AUTOINCREMENT,
                       itemName TEXT,
                       ownerID  INTEGER,
                       FOREIGN KEY (ownerID) REFERENCES users (id) ON DELETE CASCADE
                   )"""
            )
            await conn.execute(
                "CREATE INDEX IF NOT EXISTS ownerID_idx ON items(ownerID)"
            )
            await conn.commit()

    async def ensure_registered(self, user_id: typing.Union[str, int]) -> None:
        """
        Check if a user exists in the database, registering them if not found.

        Args:
            user_id: Discord user ID or unique identifier

        Example:
            >> await economy.ensure_registered(1234567890)
        """
        async with self.pool.connection() as conn:
            query = await conn.execute("SELECT id FROM users WHERE id = ?", (user_id,))
            result = await query.fetchone()

            if not result:
                await conn.execute("INSERT INTO users VALUES(?, 0, 0)", (user_id,))
                await conn.commit()

    async def get_user(self, user_id: typing.Union[str, int]) -> User:
        """
        Retrieve a user's complete economic profile including items.

        Args:
            user_id: Discord user ID or unique identifier

        Returns:
            User: User object containing balance information and items

        Raises:
            NoItemFound: If the specified user doesn't exist

        Example:
            >> user = await economy.get_user(1234567890)
            >> print(user.bank, user.wallet, user.items)
        """
        async with self.pool.connection() as conn:
            # Get user base information
            user_query = await conn.execute(
                "SELECT * FROM users WHERE id = ?", (user_id,)
            )
            user_data = await user_query.fetchone()

            if not user_data:
                raise NotFoundException(f"User {user_id} not found")

            # Get user's items
            items_query = await conn.execute(
                "SELECT * FROM items WHERE ownerID = ?", (user_id,)
            )
            items_data = await items_query.fetchall()
            items = [Item(*item) for item in items_data]

        return User(user_data[0], user_data[1], user_data[2], items)

    async def delete_user_account(self, user_id: typing.Union[str, int]) -> None:
        """
        Permanently delete a user account and all associated items.

        Args:
            user_id: Discord user ID or unique identifier

        Note:
            This action is irreversible and will remove all user data including items
            due to ON DELETE CASCADE foreign key constraint.
        """
        async with self.pool.connection() as conn:
            await conn.execute("DELETE FROM users WHERE id = ?", (user_id,))
            await conn.commit()

    async def get_all_users(self) -> typing.AsyncGenerator[User, None]:
        """
        Retrieve all users from the database as an asynchronous generator.

        Yields:
            User: Complete user objects with balances and items

        Example:
            >> async for user in economy.get_all_users():
            ...     print(f"User {user.id}: {user.bank} coins")
        """
        async with self.pool.connection() as conn:
            user_query = await conn.execute("SELECT * FROM users")
            users_data = await user_query.fetchall()

            for user in users_data:
                items_query = await conn.execute(
                    "SELECT * FROM items WHERE ownerID = ?", (user[0],)
                )
                items_data = await items_query.fetchall()
                items = [Item(*item) for item in items_data]

                yield User(user[0], user[1], user[2], items)

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
            NoItemFound: If user doesn't exist

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

        async with self.pool.connection() as conn:
            await conn.execute(
                f"UPDATE users SET {field} = {field} + ? WHERE id = ?",
                (amount, user_id),
            )
            await conn.commit()

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
            NoItemFound: If user doesn't exist

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

        async with self.pool.connection() as conn:
            if self.__ensure_positive_balance:
                balance_query = await conn.execute(
                    f"SELECT {field} FROM users WHERE id = ?", (user_id,)
                )
                balance = (await balance_query.fetchone())[0]

                if balance - amount < 0:
                    await self.set_money(user_id, field, 0)
                    return

            await conn.execute(
                f"UPDATE users SET {field} = {field} - ? WHERE id = ?",
                (amount, user_id),
            )
            await conn.commit()

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
            NoItemFound: If user doesn't exist

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

        async with self.pool.connection() as conn:
            await conn.execute(
                f"UPDATE users SET {field} = ? WHERE id = ?", (amount, user_id)
            )
            await conn.commit()

    async def add_item(self, user_id: typing.Union[str, int], item_name: str) -> None:
        """
        Add an item to a user's inventory.

        Args:
            user_id: Discord user ID or unique identifier
            item_name: Name of the item to add

        Raises:
            ItemAlreadyExists: If user already possesses this item
            NoItemFound: If user doesn't exist

        Example:
            >> await economy.add_item(1234567890, "magic_sword")
        """
        async with self.pool.connection() as conn:
            await conn.execute(
                "INSERT INTO items VALUES(NULL, ?, ?)", (item_name, user_id)
            )
            await conn.commit()

    async def remove_item(
        self, user_id: typing.Union[str, int], item_name: str
    ) -> None:
        """
        Remove an item from a user's inventory.

        Args:
            user_id: Discord user ID or unique identifier
            item_name: Name of the item to remove

        Raises:
            NoItemFound: If either user doesn't exist or item not found

        Example:
            >> await economy.remove_item(1234567890, "old_sword")
        """
        async with self.pool.connection() as conn:
            # Verify item exists
            check_query = await conn.execute(
                "SELECT id FROM items WHERE ownerID = ? AND itemName = ?",
                (user_id, item_name),
            )
            if not await check_query.fetchone():
                raise NotFoundException(
                    f"Item {item_name} not found for user {user_id}"
                )

            await conn.execute(
                "DELETE FROM items WHERE itemName = ? AND ownerID = ?",
                (item_name, user_id),
            )
            await conn.commit()
