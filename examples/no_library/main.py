import asyncio

from DiscordEconomy.Sqlite import Economy

economy = Economy()


async def main() -> None:
    await economy.ensure_registered(12345)

    await economy.add_money(12345, "bank", 500)
    await economy.add_item(12345, "pancake")

    user = await economy.get_user(12345)

    print(user)

    print(user.wallet)
    print(user.bank)

    for item in user.items:
        print(item.name)


asyncio.new_event_loop().run_until_complete(main())
