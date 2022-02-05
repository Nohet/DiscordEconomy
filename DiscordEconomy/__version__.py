from aiohttp import request
from .__init__ import __version__


async def check_for_updates() -> None:
    """Check if DiscordEconomy version is the newest one"""

    try:
        async with request(method="GET", url="https://pypi.org/pypi/DiscordEconomy/json") as res:
            _r = await res.json()

        if __version__ != _r["info"]["version"]:
            print(f"\33[1;32mNewer version of DiscordEconomy is available({_r['info']['version']})",
                  "\n\33[1;32mUpgrade to newer version using: pip install DiscordEconomy -U",
                  "\033[0m")

        return

    except Exception as e:
        print("\33[1;31mSomething went wrong when checking for updates!",
              f"\n\33[1;31mError: {e}",
              "\033[0m")
