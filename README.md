# DiscordEconomy 1.3.1
[![Downloads](https://pepy.tech/badge/discordeconomy)](https://pepy.tech/project/discordeconomy)

Discord.py, other libs, and forks(pycord, nextcord etc.) extension to create economy easily.
## Installation

You can install package directly from pypi

`pip install DiscordEconomy`
 
## Functions available

The current list of asynchronous functions available are:

```python
await is_registered(user_id)
await get_user(user_id)
await delete_user_account(user_id)
await get_all_data()
await add_money(user_id, value, amount)
await remove_money(user_id, value, amount)
await set_money(user_id, value, amount)
await add_item(user_id, item)
await remove_item(user_id, item)
 ```


 ## Important Links
 * Documentation - *soon*


## Example Usage
```python
import random

import discord
from discord.ext import commands

import DiscordEconomy


async def is_registered(ctx):
    r = await economy.is_registered(ctx.message.author.id)
    return r


client = commands.AutoShardedBot(command_prefix="?")
economy = DiscordEconomy.Economy()

is_registered = commands.check(is_registered)

items_list = {
    "Items": {
        "crystal": {
            "available": True,
            "price": 300,
            "description": "Provide description for item here"
        },
        "fishing rod": {
            "available": True,
            "price": 1200,
            "description": "Provide description for item here"
        },
        "pickaxe": {
            "available": True,
            "price": 1500,
            "description": "Provide description for item here"
        },
        "sword": {
            "available": True,
            "price": 700,
            "description": "Provide description for item here"
        },
        "dorayaki": {
            "available": True,
            "price": 12500,
            "description": "Provide description for item here"
        },
        "pancake": {
            "available": True,
            "price": 10000,
            "description": "Provide description for item here"
        }
    }}


@client.event
async def on_ready():
    print("Bot is ready!")


@client.event
async def on_command_error(ctx, error):
    embed = discord.Embed(
        colour=discord.Color.from_rgb(244, 182, 89)
    )
    if isinstance(error, commands.CommandNotFound):
        embed.add_field(name="Error", value="""This command does not exists!
                                            If you want to use shop, type ?shop""")
        await ctx.send(embed=embed)
    else:
        embed.add_field(name="Error", value=error)


@client.command()
@is_registered
async def balance(ctx: commands.Context, member: discord.Member = None):
    if not member:
        member = ctx.message.author

    user_account = await economy.get_user(member.id)

    embed = discord.Embed(
        colour=discord.Color.from_rgb(244, 182, 89)
    )
    embed.add_field(name=f"{member.display_name}'s balance", value=f"""Bank: **{user_account[1]}**
                                                                     Wallet: **{user_account[2]}**
                                                                     Items: **{user_account[3]}**""")
    embed.set_footer(text=f"Invoked by {ctx.message.author.name}", icon_url=ctx.message.author.avatar_url)
    await ctx.send(embed=embed)


@client.command()
@commands.cooldown(1, 3600, commands.BucketType.user)
@is_registered
async def reward(ctx: commands.Context):
    random_amount = random.randint(50, 150)
    await economy.add_money(ctx.message.author.id, "wallet", random_amount)
    embed = discord.Embed(
        colour=discord.Color.from_rgb(244, 182, 89)
    )
    embed.add_field(name=f"Reward", value=f"Successfully claimed reward!")
    embed.set_footer(text=f"Invoked by {ctx.message.author.name}", icon_url=ctx.message.author.avatar_url)
    await ctx.send(embed=embed)


@client.command()
@is_registered
async def coinflip(ctx: commands.Context, money: int, arg):
    arg = arg.lower()
    random_arg = random.choice(["tails", "heads"])
    multi_money = money * 2
    r = await economy.get_user(ctx.message.author.id)
    r = r[1]
    embed = discord.Embed(
        colour=discord.Color.from_rgb(244, 182, 89)
    )
    if r >= money:
        if arg == random_arg:
            await economy.add_money(ctx.message.author.id, "bank", multi_money)

            embed.add_field(name="Coinflip", value=f"You won coinflip! - {random_arg}")
            embed.set_footer(text=f"Invoked by {ctx.message.author.name}", icon_url=ctx.message.author.avatar_url)
            await ctx.send(embed=embed)
        else:
            await economy.remove_money(ctx.message.author.id, "bank", money)

            embed.add_field(name="Coinflip", value=f"You lost coinflip! - {random_arg}")
            embed.set_footer(text=f"Invoked by {ctx.message.author.name}", icon_url=ctx.message.author.avatar_url)
            await ctx.send(embed=embed)

    else:
        embed.add_field(name="Coinflip", value=f"You don't have enough money!")
        embed.set_footer(text=f"Invoked by {ctx.message.author.name}", icon_url=ctx.message.author.avatar_url)
        await ctx.send(embed=embed)


@client.command()
@is_registered
async def slots(ctx: commands.Context, money: int):
    money_multi = money * 2
    random_slots_data = ["", "", "",
                         "", "", "",
                         "", "", ""]
    i = 0
    for _ in random_slots_data:
        random_slots_data[i] = random.choice([":tada:", ":cookie:", ":large_blue_diamond:",
                                              ":money_with_wings:", ":moneybag:", ":cherries:"])

        i += 1
        if i == len(random_slots_data):
            break
    r = await economy.get_user(ctx.message.author.id)
    r = r[1]
    embed = discord.Embed(
        colour=discord.Color.from_rgb(244, 182, 89)
    )
    if r >= money:

        embed.add_field(name="Slots", value=f"""{random_slots_data[0]} | {random_slots_data[1]} | {random_slots_data[2]}
                                                {random_slots_data[3]} | {random_slots_data[4]} | {random_slots_data[5]}
                                                {random_slots_data[6]} | {random_slots_data[7]} | {random_slots_data[8]}
                                            """)
        embed.set_footer(text=f"Invoked by {ctx.message.author.name}", icon_url=ctx.message.author.avatar_url)
        await ctx.send(embed=embed)
        if random_slots_data[3] == random_slots_data[4] and random_slots_data[5] == random_slots_data[3]:
            await economy.add_money(ctx.message.author.id, "bank", money_multi)
            await ctx.send("You won!")
        else:
            await economy.remove_money(ctx.message.author.id, "bank", money)
            await ctx.send("You loss!")

    else:
        embed.add_field(name="Slots", value=f"You don't have enough money!")
        embed.set_footer(text=f"Invoked by {ctx.message.author.name}", icon_url=ctx.message.author.avatar_url)
        await ctx.send(embed=embed)


@client.command()
@is_registered
async def withdraw(ctx: commands.Context, money: int):
    r = await economy.get_user(ctx.message.author.id)
    r = r[1]
    embed = discord.Embed(
        colour=discord.Color.from_rgb(244, 182, 89)
    )
    if r >= money:
        await economy.add_money(ctx.message.author.id, "wallet", money)
        await economy.remove_money(ctx.message.author.id, "bank", money)

        embed.add_field(name="Withdraw", value=f"Successfully withdrawn {money} money!")
        embed.set_footer(text=f"Invoked by {ctx.message.author.name}", icon_url=ctx.message.author.avatar_url)
        await ctx.send(embed=embed)

    else:

        embed.add_field(name="Withdraw", value=f"You don't have enough money to withdraw!")
        embed.set_footer(text=f"Invoked by {ctx.message.author.name}", icon_url=ctx.message.author.avatar_url)
        await ctx.send(embed=embed)


@client.command()
@is_registered
async def deposit(ctx: commands.Context, money: int):
    r = await economy.get_user(ctx.message.author.id)
    r = r[2]
    embed = discord.Embed(
        colour=discord.Color.from_rgb(244, 182, 89)
    )
    if r >= money:
        await economy.add_money(ctx.message.author.id, "bank", money)
        await economy.remove_money(ctx.message.author.id, "wallet", money)

        embed.add_field(name="Deposit", value=f"Successfully deposited {money} money!")
        embed.set_footer(text=f"Invoked by {ctx.message.author.name}", icon_url=ctx.message.author.avatar_url)
        await ctx.send(embed=embed)

    else:

        embed.add_field(name="Deposit", value=f"You don't have enough money to deposit!")
        embed.set_footer(text=f"Invoked by {ctx.message.author.name}", icon_url=ctx.message.author.avatar_url)
        await ctx.send(embed=embed)


@client.group(invoke_without_command=True)
@is_registered
async def shop(ctx: commands.Context):
    embed = discord.Embed(
        colour=discord.Color.from_rgb(244, 182, 89)
    )

    embed.add_field(name="Shop", value=f"In the shop you can buy and sell items!", inline=False)
    embed.add_field(name="Available commands", value=f"""?shop buy <item>
                                                         ?shop sell <item>
                                                         ?shop items""", inline=False)
    embed.set_footer(text=f"Invoked by {ctx.message.author.name}", icon_url=ctx.message.author.avatar_url)
    await ctx.send(embed=embed)


@shop.command()
@is_registered
async def items(ctx: commands.Context):
    embed = discord.Embed(
        colour=discord.Color.from_rgb(244, 182, 89)
    )
    embed.set_author(name="Items")
    for item in items_list["Items"].items():
        embed.add_field(name=item[0].capitalize(), value=item[1]["description"] + "\n_ _" + "\n" +
                                                         f"Price: **{item[1]['price']}**" + "\n"
                                                         + f"Available: **{item[1]['available']}**")

        embed.set_footer(text=f"Invoked by {ctx.message.author.name}", icon_url=ctx.message.author.avatar_url)
    await ctx.send(embed=embed)


@shop.command()
@is_registered
async def buy(ctx: commands.Context, *, _item: str):
    _item = _item.lower()
    _cache = []
    embed = discord.Embed(
        colour=discord.Color.from_rgb(244, 182, 89)
    )
    for item in items_list["Items"].items():
        if item[0] == _item:
            _cache.append(item[0])

            r = await economy.get_user(ctx.message.author.id)

            user_balance = r[1]
            your_items = r[3]
            your_items = your_items.split(" | ")
            if item[0] in your_items:
                embed.add_field(name="Error", value=f"You already have that item!")
                embed.set_footer(text=f"Invoked by {ctx.message.author.name}", icon_url=ctx.message.author.avatar_url)
                await ctx.send(embed=embed)
                return

            if user_balance >= item[1]["price"]:
                await economy.add_item(ctx.message.author.id, item[0])
                await economy.remove_money(ctx.message.author.id, "bank", item[1]["price"])

                embed.add_field(name="Success", value=f"Successfully bought **{item[0]}**!")
                embed.set_footer(text=f"Invoked by {ctx.message.author.name}",
                                 icon_url=ctx.message.author.avatar_url)
                await ctx.send(embed=embed)

            else:

                embed.add_field(name="Error", value=f"You don't have enought money to buy this item!")
                embed.set_footer(text=f"Invoked by {ctx.message.author.name}",
                                 icon_url=ctx.message.author.avatar_url)
                await ctx.send(embed=embed)
            break

    if len(_cache) <= 0:
        embed.add_field(name="Error", value="Item with that name does not exists!")
        await ctx.send(embed=embed)


@shop.command()
@is_registered
async def sell(ctx: commands.Context, *, _item: str):
    r = await economy.get_user(ctx.message.author.id)

    _item = _item.lower()

    your_items = r[3]
    your_items_list = your_items.split(" | ")

    embed = discord.Embed(
        colour=discord.Color.from_rgb(244, 182, 89)
    )

    if _item in your_items_list:
        for item in items_list["Items"].items():
            if item[0] == _item:
                item_prc = item[1]["price"] / 2

                await economy.add_money(ctx.message.author.id, "bank", item_prc)
                await economy.remove_item(ctx.message.author.id, item[0])

                embed.add_field(name="Success", value=f"Successfully sold **{item[0]}**!")
                await ctx.send(embed=embed)
                break
    else:

        embed.add_field(name="Error", value=f"You don't have this item!")
        await ctx.send(embed=embed)

# Pass here token as string
client.run()
```
