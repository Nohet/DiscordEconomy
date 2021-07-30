# DiscordEconomy 1.2
[![Downloads](https://pepy.tech/badge/discordeconomy)](https://pepy.tech/project/discordeconomy)

Discord.py extension to create economy easily.

[![Donate](https://i.imgur.com/BCr1sIV.png)](https://paypal.me/DiscordEconomy)

## Installation

You can install package directly from pypi

`pip install DiscordEconomy`
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

available_items = ["crystal", "fishing rod", "pickaxe", "sword", "dorayaki",
                   "pancake"]
items_price = ["crystal-price | 300", "fishing rod-price | 1200", "pickaxe-price | 1500",
               "sword-price | 700", "dorayaki-price | 12500", "pancake-price | 10000"]


@client.event
async def on_ready():
    print("Bot is ready!")


@client.event
async def on_command_error(ctx, error):
    await ctx.send(error)


@client.command()
@is_registered
async def balance(ctx, member: discord.Member = None):
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
async def reward(ctx):
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
async def coinflip(ctx, money: int, arg):
    arg = arg.lower()
    random_arg = random.choice(["tails", "heads"])
    multi_money = money * 2
    r = await economy.get_user(ctx.message.author.id)
    r = r[1]
    if r >= money:
        if arg == random_arg:
            await economy.add_money(ctx.message.author.id, "bank", multi_money)
            embed = discord.Embed(
                colour=discord.Color.from_rgb(244, 182, 89)
            )
            embed.add_field(name="Coinflip", value=f"You won coinflip! - {random_arg}")
            embed.set_footer(text=f"Invoked by {ctx.message.author.name}", icon_url=ctx.message.author.avatar_url)
            await ctx.send(embed=embed)
        else:
            await economy.remove_money(ctx.message.author.id, "bank", money)
            embed = discord.Embed(
                colour=discord.Color.from_rgb(244, 182, 89)
            )
            embed.add_field(name="Coinflip", value=f"You lost coinflip! - {random_arg}")
            embed.set_footer(text=f"Invoked by {ctx.message.author.name}", icon_url=ctx.message.author.avatar_url)
            await ctx.send(embed=embed)

    else:
        embed = discord.Embed(
            colour=discord.Color.from_rgb(244, 182, 89)
        )
        embed.add_field(name="Coinflip", value=f"You don't have enough money!")
        embed.set_footer(text=f"Invoked by {ctx.message.author.name}", icon_url=ctx.message.author.avatar_url)
        await ctx.send(embed=embed)


@client.command()
@is_registered
async def slots(ctx, money: int):
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
    if r >= money:
        embed = discord.Embed(
            colour=discord.Color.from_rgb(244, 182, 89)
        )
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
        embed = discord.Embed(
            colour=discord.Color.from_rgb(244, 182, 89)
        )
        embed.add_field(name="Slots", value=f"You don't have enough money!")
        embed.set_footer(text=f"Invoked by {ctx.message.author.name}", icon_url=ctx.message.author.avatar_url)
        await ctx.send(embed=embed)


@client.command()
@is_registered
async def withdraw(ctx, money: int):
    r = await economy.get_user(ctx.message.author.id)
    r = r[1]
    if r >= money:
        await economy.add_money(ctx.message.author.id, "wallet", money)
        await economy.remove_money(ctx.message.author.id, "bank", money)
        embed = discord.Embed(
            colour=discord.Color.from_rgb(244, 182, 89)
        )

        embed.add_field(name="Withdraw", value=f"Successfully withdrawn {money} money!")
        embed.set_footer(text=f"Invoked by {ctx.message.author.name}", icon_url=ctx.message.author.avatar_url)
        await ctx.send(embed=embed)

    else:
        embed = discord.Embed(
            colour=discord.Color.from_rgb(244, 182, 89)
        )

        embed.add_field(name="Withdraw", value=f"You don't have enough money to withdraw!")
        embed.set_footer(text=f"Invoked by {ctx.message.author.name}", icon_url=ctx.message.author.avatar_url)
        await ctx.send(embed=embed)


@client.command()
@is_registered
async def deposit(ctx, money: int):
    r = await economy.get_user(ctx.message.author.id)
    r = r[2]
    if r >= money:
        await economy.add_money(ctx.message.author.id, "bank", money)
        await economy.remove_money(ctx.message.author.id, "wallet", money)
        embed = discord.Embed(
            colour=discord.Color.from_rgb(244, 182, 89)
        )

        embed.add_field(name="Deposit", value=f"Successfully deposited {money} money!")
        embed.set_footer(text=f"Invoked by {ctx.message.author.name}", icon_url=ctx.message.author.avatar_url)
        await ctx.send(embed=embed)

    else:
        embed = discord.Embed(
            colour=discord.Color.from_rgb(244, 182, 89)
        )

        embed.add_field(name="Deposit", value=f"You don't have enough money to deposit!")
        embed.set_footer(text=f"Invoked by {ctx.message.author.name}", icon_url=ctx.message.author.avatar_url)
        await ctx.send(embed=embed)


@client.command()
@is_registered
async def buy_item(ctx, *, item):
    r = await economy.get_user(ctx.message.author.id)
    user_balance = r[1]
    your_items = r[3]
    your_items = your_items.split(" | ")
    if item in your_items:
        embed = discord.Embed(
            colour=discord.Color.from_rgb(244, 182, 89)
        )

        embed.add_field(name="Error", value=f"You already have that item!")
        embed.set_footer(text=f"Invoked by {ctx.message.author.name}", icon_url=ctx.message.author.avatar_url)
        await ctx.send(embed=embed)
        return

    if item in available_items:
        for item_price in items_price:
            if str(item) in item_price:
                item_prc = item_price.split(" | ")
                item_prc = item_prc[1].replace(" ", "")
                if user_balance >= int(item_prc):
                    await economy.add_item(ctx.message.author.id, item)
                    await economy.remove_money(ctx.message.author.id, "bank", user_balance - int(item_prc))
                    embed = discord.Embed(
                        colour=discord.Color.from_rgb(244, 182, 89)
                    )

                    embed.add_field(name="Success", value=f"Successfully bought **{item}**!")
                    embed.set_footer(text=f"Invoked by {ctx.message.author.name}",
                                     icon_url=ctx.message.author.avatar_url)
                    await ctx.send(embed=embed)
                else:
                    embed = discord.Embed(
                        colour=discord.Color.from_rgb(244, 182, 89)
                    )

                    embed.add_field(name="Error", value=f"You don't have enought money to buy this item!")
                    embed.set_footer(text=f"Invoked by {ctx.message.author.name}",
                                     icon_url=ctx.message.author.avatar_url)
                    await ctx.send(embed=embed)
    else:
        embed = discord.Embed(
            colour=discord.Color.from_rgb(244, 182, 89)
        )

        embed.add_field(name="Error", value="This item does not exist!")
        embed.set_footer(text=f"Invoked by {ctx.message.author.name}", icon_url=ctx.message.author.avatar_url)
        await ctx.send(embed=embed)


@client.command()
@is_registered
async def sell_item(ctx, *, item):
    r = await economy.get_user(ctx.message.author.id)
    your_items = r[3]
    your_items_list = your_items.split(" | ")
    if item in your_items_list:
        for item_price in items_price:
            if str(item) in item_price:
                item_prc = item_price.split(" | ")
                item_prc = item_prc[1].replace(" ", "")
                item_prc = int(item_prc) / 2
                await economy.add_money(ctx.message.author.id, "bank", item_prc)
                await economy.remove_item(ctx.message.author.id, item)
                embed = discord.Embed(
                    colour=discord.Color.from_rgb(244, 182, 89)
                )

                embed.add_field(name="Success", value=f"Successfully sold **{item}**!")
                await ctx.send(embed=embed)
    else:
        embed = discord.Embed(
            colour=discord.Color.from_rgb(244, 182, 89)
        )

        embed.add_field(name="Error", value=f"You don't have this item!")
        await ctx.send(embed=embed)


@client.command()
@is_registered
async def items(ctx):
    embed = discord.Embed(
        colour=discord.Color.from_rgb(244, 182, 89)
    )

    embed.add_field(name="Available items", value=str.join(", ", available_items))
    await ctx.send(embed=embed)


client.run()
```



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
 * Donate - [Click Here](https://paypal.me/DiscordEconomy)           
 * Documentation - *soon*

