import asyncio

from DiscordEconomy.Sqlite import Economy

eco = Economy()


async def main():
    async for user in eco.get_all_data():
        print(user)

asyncio.get_event_loop().run_until_complete(main())