import asyncio
import pytest

from DiscordEconomy.Sqlite import Economy
from DiscordEconomy.exceptions import (
    EnsurePositiveBalanceException,
    NegativeAmountException,
    NotFoundException,
)


pytestmark = pytest.mark.asyncio


async def test_registration_and_get_user(economy, user_id):
    # Not registered yet -> ensure_registered should create
    await economy.ensure_registered(user_id)
    user = await economy.get_user(user_id)
    assert user.id == user_id
    assert user.bank == 0
    assert user.wallet == 0
    assert user.items == []


async def test_add_and_remove_money_wallet(economy, user_id):
    await economy.ensure_registered(user_id)

    # add
    await economy.add_money(user_id, "wallet", 150)
    user = await economy.get_user(user_id)
    assert user.wallet == 150

    # remove with positive-balance enforcement: should drop to 0 not negative
    await economy.remove_money(user_id, "wallet", 200)
    user = await economy.get_user(user_id)
    assert user.wallet == 0


async def test_add_and_remove_money_bank(economy, user_id):
    await economy.ensure_registered(user_id)

    await economy.add_money(user_id, "bank", 100)
    user = await economy.get_user(user_id)
    assert user.bank == 100

    await economy.remove_money(user_id, "bank", 40)
    user = await economy.get_user(user_id)
    assert user.bank == 60


async def test_negative_amount_rejected(economy, user_id):
    await economy.ensure_registered(user_id)

    with pytest.raises(NegativeAmountException):
        await economy.add_money(user_id, "bank", -1)

    with pytest.raises(NegativeAmountException):
        await economy.remove_money(user_id, "wallet", -5)


async def test_set_money_constraints(economy, user_id):
    await economy.ensure_registered(user_id)

    # enforce positive balance: negative set is rejected
    with pytest.raises(EnsurePositiveBalanceException):
        await economy.set_money(user_id, "bank", -10)

    # valid set
    await economy.set_money(user_id, "bank", 999.5)
    user = await economy.get_user(user_id)
    assert user.bank == 999.5


async def test_items_crud(economy, user_id):
    await economy.ensure_registered(user_id)

    await economy.add_item(user_id, "sword")
    await economy.add_item(user_id, "potion")

    user = await economy.get_user(user_id)
    names = [i.name for i in user.items]
    assert set(names) == {"sword", "potion"}

    await economy.remove_item(user_id, "sword")

    user = await economy.get_user(user_id)
    names = [i.name for i in user.items]
    assert set(names) == {"potion"}

    with pytest.raises(NotFoundException):
        await economy.remove_item(user_id, "not-exists")


async def test_get_all_users_generator(economy):
    # create some
    for uid in (1, 2, 3):
        await economy.ensure_registered(uid)
        await economy.add_money(uid, "bank", uid * 10)

    seen = {}
    async for u in economy.get_all_users():
        seen[u.id] = u.bank

    assert seen[1] == 10
    assert seen[2] == 20
    assert seen[3] == 30


async def test_delete_user_account_cascade(economy, user_id):
    await economy.ensure_registered(user_id)
    await economy.add_item(user_id, "x")
    await economy.add_item(user_id, "y")

    # delete
    await economy.delete_user_account(user_id)

    with pytest.raises(NotFoundException):
        await economy.get_user(user_id)
