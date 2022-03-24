import asyncio

import DiscordEconomy

economy = DiscordEconomy.Economy()


async def main() -> None:
    await economy.is_registered(12345)
    user = await economy.get_user(12345)


    print(user)
    # print(user.wallet)
    # print(user.bank)
    # print(user.items)


asyncio.new_event_loop().run_until_complete(main())
