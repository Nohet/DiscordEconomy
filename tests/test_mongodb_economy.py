import asyncio
import pytest

from DiscordEconomy.MongoDB import Economy
from DiscordEconomy.exceptions import (
    EnsurePositiveBalanceException,
    NegativeAmountException,
    NotFoundException,
    ItemAlreadyExists,
)


pytestmark = pytest.mark.asyncio


async def test_registration_and_get_user(mongodb_economy, user_id):
    # Not registered yet -> ensure_registered should create
    await mongodb_economy.ensure_registered(user_id)
    user = await mongodb_economy.get_user(user_id)
    assert user.id == user_id
    assert user.bank == 0
    assert user.wallet == 0
    assert user.items == []


async def test_add_and_remove_money_wallet(mongodb_economy, user_id):
    await mongodb_economy.ensure_registered(user_id)

    # add
    await mongodb_economy.add_money(user_id, "wallet", 150)
    user = await mongodb_economy.get_user(user_id)
    assert user.wallet == 150

    # remove with positive-balance enforcement: should drop to 0 not negative
    await mongodb_economy.remove_money(user_id, "wallet", 200)
    user = await mongodb_economy.get_user(user_id)
    assert user.wallet == 0


async def test_add_and_remove_money_bank(mongodb_economy, user_id):
    await mongodb_economy.ensure_registered(user_id)

    await mongodb_economy.add_money(user_id, "bank", 100)
    user = await mongodb_economy.get_user(user_id)
    assert user.bank == 100

    await mongodb_economy.remove_money(user_id, "bank", 40)
    user = await mongodb_economy.get_user(user_id)
    assert user.bank == 60


async def test_negative_amount_rejected(mongodb_economy, user_id):
    await mongodb_economy.ensure_registered(user_id)

    with pytest.raises(NegativeAmountException):
        await mongodb_economy.add_money(user_id, "bank", -1)

    with pytest.raises(NegativeAmountException):
        await mongodb_economy.remove_money(user_id, "wallet", -5)


async def test_invalid_field_rejected(mongodb_economy, user_id):
    await mongodb_economy.ensure_registered(user_id)

    with pytest.raises(ValueError):
        await mongodb_economy.add_money(user_id, "invalid_field", 100)

    with pytest.raises(ValueError):
        await mongodb_economy.remove_money(user_id, "invalid_field", 50)

    with pytest.raises(ValueError):
        await mongodb_economy.set_money(user_id, "invalid_field", 200)


async def test_set_money_constraints(mongodb_economy, user_id):
    await mongodb_economy.ensure_registered(user_id)

    # enforce positive balance: negative set is rejected
    with pytest.raises(EnsurePositiveBalanceException):
        await mongodb_economy.set_money(user_id, "bank", -10)

    # valid set
    await mongodb_economy.set_money(user_id, "bank", 999.5)
    user = await mongodb_economy.get_user(user_id)
    assert user.bank == 999.5


async def test_items_crud(mongodb_economy, user_id):
    await mongodb_economy.ensure_registered(user_id)

    await mongodb_economy.add_item(user_id, "sword")
    await mongodb_economy.add_item(user_id, "potion")

    user = await mongodb_economy.get_user(user_id)
    names = [i.name for i in user.items]
    assert set(names) == {"sword", "potion"}

    # Test adding duplicate item should raise ItemAlreadyExists
    with pytest.raises(ItemAlreadyExists):
        await mongodb_economy.add_item(user_id, "sword")

    await mongodb_economy.remove_item(user_id, "sword")

    user = await mongodb_economy.get_user(user_id)
    names = [i.name for i in user.items]
    assert set(names) == {"potion"}

    with pytest.raises(NotFoundException):
        await mongodb_economy.remove_item(user_id, "not-exists")


async def test_get_all_users_generator(mongodb_economy):
    # create some users
    for uid in (1, 2, 3):
        await mongodb_economy.ensure_registered(uid)
        await mongodb_economy.add_money(uid, "bank", uid * 10)

    seen = {}
    async for u in mongodb_economy.get_all_users():
        seen[u.id] = u.bank

    assert seen[1] == 10
    assert seen[2] == 20
    assert seen[3] == 30


async def test_delete_user_account(mongodb_economy, user_id):
    await mongodb_economy.ensure_registered(user_id)
    await mongodb_economy.add_item(user_id, "x")
    await mongodb_economy.add_item(user_id, "y")

    # verify user exists
    user = await mongodb_economy.get_user(user_id)
    assert len(user.items) == 2

    # delete
    await mongodb_economy.delete_user_account(user_id)

    # user should not exist anymore
    with pytest.raises(NotFoundException):
        await mongodb_economy.get_user(user_id)


async def test_get_nonexistent_user(mongodb_economy):
    # Try to get user that doesn't exist
    with pytest.raises(NotFoundException):
        await mongodb_economy.get_user(999999)


async def test_ensure_positive_balance_disabled(user_id):
    """Test behavior when ensure_positive_balance is disabled"""
    # This test would require a separate fixture with ensure_positive_balance=False
    # For now, we'll skip this test and note it for future implementation
    pytest.skip("Requires fixture with ensure_positive_balance=False")


async def test_float_amounts(mongodb_economy, user_id):
    """Test that float amounts work correctly"""
    await mongodb_economy.ensure_registered(user_id)

    # Test float addition
    await mongodb_economy.add_money(user_id, "wallet", 123.45)
    user = await mongodb_economy.get_user(user_id)
    assert user.wallet == 123.45

    # Test float removal
    await mongodb_economy.remove_money(user_id, "wallet", 23.45)
    user = await mongodb_economy.get_user(user_id)
    assert user.wallet == 100.0

    # Test float setting
    await mongodb_economy.set_money(user_id, "bank", 555.55)
    user = await mongodb_economy.get_user(user_id)
    assert user.bank == 555.55


async def test_large_user_id(mongodb_economy):
    """Test with large user IDs (Discord snowflakes can be very large)"""
    large_user_id = 1234567890123456789

    await mongodb_economy.ensure_registered(large_user_id)
    await mongodb_economy.add_money(large_user_id, "wallet", 1000)

    user = await mongodb_economy.get_user(large_user_id)
    assert user.id == large_user_id
    assert user.wallet == 1000


async def test_multiple_users_items(mongodb_economy):
    """Test that items are properly isolated between users"""
    user1_id = 111
    user2_id = 222

    await mongodb_economy.ensure_registered(user1_id)
    await mongodb_economy.ensure_registered(user2_id)

    # Add same item name to both users
    await mongodb_economy.add_item(user1_id, "sword")
    await mongodb_economy.add_item(user2_id, "sword")

    user1 = await mongodb_economy.get_user(user1_id)
    user2 = await mongodb_economy.get_user(user2_id)

    assert len(user1.items) == 1
    assert len(user2.items) == 1
    assert user1.items[0].name == "sword"
    assert user2.items[0].name == "sword"
    assert user1.items[0].owner_id == user1_id
    assert user2.items[0].owner_id == user2_id

    # Remove item from user1, user2 should still have it
    await mongodb_economy.remove_item(user1_id, "sword")

    user1 = await mongodb_economy.get_user(user1_id)
    user2 = await mongodb_economy.get_user(user2_id)

    assert len(user1.items) == 0
    assert len(user2.items) == 1


async def test_string_user_id(mongodb_economy):
    """Test that string user IDs work correctly"""
    string_user_id = "test_user_123"

    await mongodb_economy.ensure_registered(string_user_id)
    await mongodb_economy.add_money(string_user_id, "bank", 500)
    await mongodb_economy.add_item(string_user_id, "shield")

    user = await mongodb_economy.get_user(string_user_id)
    assert user.id == string_user_id
    assert user.bank == 500
    assert len(user.items) == 1
    assert user.items[0].name == "shield"
