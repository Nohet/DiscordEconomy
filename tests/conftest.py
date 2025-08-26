import asyncio
import pytest
import os

from DiscordEconomy.Sqlite import Economy


@pytest.fixture()
def economy(monkeypatch, tmp_path):
    db_file = tmp_path / "test_economy.db"

    async def _noop():
        return None

    monkeypatch.setattr(
        "DiscordEconomy.__version__.check_for_updates", _noop, raising=False
    )
    monkeypatch.setattr("DiscordEconomy.Sqlite.check_for_updates", _noop, raising=False)

    e = Economy(database_name=str(db_file), ensure_positive_balance=True)

    asyncio.get_event_loop().run_until_complete(e.ensure_registered(0))
    return e


@pytest.fixture()
async def mongodb_economy(monkeypatch):
    """
    MongoDB fixture for testing.

    Uses a test database and cleans up after each test.
    Requires MongoDB to be running locally or via Docker.
    """
    from DiscordEconomy.MongoDB import Economy as MongoEconomy

    async def _noop():
        return None

    monkeypatch.setattr(
        "DiscordEconomy.__version__.check_for_updates", _noop, raising=False
    )
    monkeypatch.setattr(
        "DiscordEconomy.MongoDB.check_for_updates", _noop, raising=False
    )

    mongo_url = os.getenv("MONGODB_TEST_URL", "mongodb://localhost:27017")
    test_db_name = "test_discord_economy"
    test_collection = "test_economy"

    try:
        economy = MongoEconomy(
            mongo_url=mongo_url,
            database_name=test_db_name,
            collection=test_collection,
            ensure_positive_balance=True,
        )

        yield economy

    finally:
        try:
            await economy._Economy__client.drop_database(test_db_name)
        except Exception:
            pass


@pytest.fixture()
def user_id():
    return 1234567890
