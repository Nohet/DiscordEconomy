import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from DiscordEconomy.MongoDB import Economy
from DiscordEconomy.exceptions import (
    NotFoundException,
    ItemAlreadyExists,
    NegativeAmountException,
)


class TestMongoDBEconomyMocked:
    """
    Tests for MongoDB Economy using mocks.
    These tests don't require a real MongoDB instance.
    """

    @pytest.fixture
    def mock_motor_client(self):
        """Mock motor client for testing without MongoDB"""
        with patch(
            "DiscordEconomy.MongoDB.motor_asyncio.AsyncIOMotorClient"
        ) as mock_client:
            mock_instance = MagicMock()
            mock_client.return_value = mock_instance

            mock_db = MagicMock()
            mock_collection = AsyncMock()
            mock_instance.__getitem__.return_value = mock_db
            mock_db.__getitem__.return_value = mock_collection

            yield mock_client, mock_instance, mock_collection

    @pytest.fixture
    def mock_economy(self, mock_motor_client, monkeypatch):
        """Create Economy instance with mocked MongoDB"""

        async def _noop():
            return None

        monkeypatch.setattr(
            "DiscordEconomy.MongoDB.check_for_updates", _noop, raising=False
        )

        mock_client, mock_instance, mock_collection = mock_motor_client

        economy = Economy(
            mongo_url="mongodb://mock:27017",
            database_name="test_db",
            ensure_positive_balance=True,
        )

        economy._Economy__collection = mock_collection
        economy._Economy__client = mock_instance

        return economy, mock_collection

    @pytest.mark.asyncio
    async def test_ensure_registered_new_user(self, mock_economy):
        """Test registering a new user"""
        economy, mock_collection = mock_economy

        mock_collection.find_one.return_value = None
        mock_collection.insert_one = AsyncMock()

        await economy.ensure_registered(123)

        mock_collection.find_one.assert_called_once_with({"_id": 123})
        mock_collection.insert_one.assert_called_once_with(
            {"_id": 123, "bank": 0, "wallet": 0, "items": []}
        )

    @pytest.mark.asyncio
    async def test_ensure_registered_existing_user(self, mock_economy):
        """Test registering an existing user"""
        economy, mock_collection = mock_economy

        mock_collection.find_one.return_value = {
            "_id": 123,
            "bank": 100,
            "wallet": 50,
            "items": ["sword"],
        }
        mock_collection.insert_one = AsyncMock()

        await economy.ensure_registered(123)

        mock_collection.find_one.assert_called_once_with({"_id": 123})
        mock_collection.insert_one.assert_not_called()

    @pytest.mark.asyncio
    async def test_get_user_exists(self, mock_economy):
        """Test getting an existing user"""
        economy, mock_collection = mock_economy

        mock_user_data = {
            "_id": 123,
            "bank": 500,
            "wallet": 200,
            "items": ["sword", "potion"],
        }
        mock_collection.find_one.return_value = mock_user_data

        user = await economy.get_user(123)

        assert user.id == 123
        assert user.bank == 500
        assert user.wallet == 200
        assert len(user.items) == 2
        assert user.items[0].name == "sword"
        assert user.items[1].name == "potion"

    @pytest.mark.asyncio
    async def test_get_user_not_exists(self, mock_economy):
        """Test getting a non-existent user"""
        economy, mock_collection = mock_economy

        mock_collection.find_one.return_value = None

        with pytest.raises(NotFoundException):
            await economy.get_user(999)

    @pytest.mark.asyncio
    async def test_add_money_valid(self, mock_economy):
        """Test adding money with valid parameters"""
        economy, mock_collection = mock_economy

        mock_collection.find_one.side_effect = [
            None,
            {
                "_id": 123,
                "bank": 100,
                "wallet": 50,
                "items": [],
            },
        ]
        mock_collection.insert_one = AsyncMock()
        mock_collection.update_one = AsyncMock()

        await economy.add_money(123, "wallet", 150)

        mock_collection.update_one.assert_called_once_with(
            {"_id": 123}, {"$set": {"wallet": 200}}
        )

    @pytest.mark.asyncio
    async def test_add_money_negative_amount(self, mock_economy):
        """Test adding negative amount raises exception"""
        economy, mock_collection = mock_economy

        with pytest.raises(NegativeAmountException):
            await economy.add_money(123, "wallet", -100)

    @pytest.mark.asyncio
    async def test_add_money_invalid_field(self, mock_economy):
        """Test adding money to invalid field raises exception"""
        economy, mock_collection = mock_economy

        with pytest.raises(ValueError):
            await economy.add_money(123, "invalid_field", 100)

    @pytest.mark.asyncio
    async def test_add_item_new(self, mock_economy):
        """Test adding a new item"""
        economy, mock_collection = mock_economy

        mock_collection.find_one.side_effect = [
            {"_id": 123, "bank": 0, "wallet": 0, "items": []},
            {"_id": 123, "bank": 0, "wallet": 0, "items": []},
        ]
        mock_collection.update_one = AsyncMock()

        await economy.add_item(123, "sword")

        mock_collection.update_one.assert_called_once_with(
            {"_id": 123}, {"$set": {"items": ["sword"]}}
        )

    @pytest.mark.asyncio
    async def test_add_item_duplicate(self, mock_economy):
        """Test adding duplicate item raises exception"""
        economy, mock_collection = mock_economy

        mock_collection.find_one.side_effect = [
            {
                "_id": 123,
                "bank": 0,
                "wallet": 0,
                "items": ["sword"],
            },
            {"_id": 123, "bank": 0, "wallet": 0, "items": ["sword"]},
        ]

        with pytest.raises(ItemAlreadyExists):
            await economy.add_item(123, "sword")

    @pytest.mark.asyncio
    async def test_remove_item_exists(self, mock_economy):
        """Test removing an existing item"""
        economy, mock_collection = mock_economy

        mock_collection.find_one.side_effect = [
            {
                "_id": 123,
                "bank": 0,
                "wallet": 0,
                "items": ["sword", "potion"],
            },
            {
                "_id": 123,
                "bank": 0,
                "wallet": 0,
                "items": ["sword", "potion"],
            },
        ]
        mock_collection.update_one = AsyncMock()

        await economy.remove_item(123, "sword")

        mock_collection.update_one.assert_called_once_with(
            {"_id": 123}, {"$set": {"items": ["potion"]}}
        )

    @pytest.mark.asyncio
    async def test_remove_item_not_exists(self, mock_economy):
        """Test removing non-existent item raises exception"""
        economy, mock_collection = mock_economy

        mock_collection.find_one.side_effect = [
            {"_id": 123, "bank": 0, "wallet": 0, "items": []},
            {"_id": 123, "bank": 0, "wallet": 0, "items": []},
        ]

        with pytest.raises(NotFoundException):
            await economy.remove_item(123, "sword")

    @pytest.mark.asyncio
    async def test_delete_user_account(self, mock_economy):
        """Test deleting user account"""
        economy, mock_collection = mock_economy

        mock_collection.delete_one = AsyncMock()

        await economy.delete_user_account(123)

        mock_collection.delete_one.assert_called_once_with({"_id": 123})
