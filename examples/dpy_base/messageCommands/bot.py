import asyncio
import random

import discord
from discord.ext import commands

import DiscordEconomy

# Pass here token as string
BOT_TOKEN = ""

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

client = commands.Bot(command_prefix="?", intents=intents)
economy = DiscordEconomy.Economy()


async def is_registered(ctx):
    r = await economy.is_registered(ctx.message.author.id)
    return r


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

        await ctx.send(embed=embed)


@client.command()
async def balance(ctx: commands.Context, member: discord.Member = None):
    member = member or ctx.message.author

    await economy.is_registered(member.id)
    user_account = await economy.get_user(member.id)

    embed = discord.Embed(
        colour=discord.Color.from_rgb(244, 182, 89)
    )
    embed.add_field(name=f"{member.display_name}'s balance", value=f"""Bank: **{user_account.bank}**
                                                                     Wallet: **{user_account.wallet}**
                                                                     Items: **{', '.join(user_account.items)}**""")
    embed.set_footer(text=f"Invoked by {ctx.message.author.name}", icon_url=ctx.message.author.avatar.url)
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
    embed.set_footer(text=f"Invoked by {ctx.message.author.name}", icon_url=ctx.message.author.avatar.url)
    await ctx.send(embed=embed)


@client.command()
@is_registered
async def coinflip(ctx: commands.Context, money: int, arg: str):
    arg = arg.lower()
    random_arg = random.choice(["tails", "heads"])
    multi_money = money * 2
    r = await economy.get_user(ctx.message.author.id)
    embed = discord.Embed(
        colour=discord.Color.from_rgb(244, 182, 89)
    )
    if r.bank >= money:
        if arg == random_arg:
            await economy.add_money(ctx.message.author.id, "wallet", multi_money)

            embed.add_field(name="Coinflip", value=f"You won coinflip! - {random_arg}")
            embed.set_footer(text=f"Invoked by {ctx.message.author.name}", icon_url=ctx.message.author.avatar.url)
            await ctx.send(embed=embed)
        else:
            await economy.remove_money(ctx.message.author.id, "bank", money)

            embed.add_field(name="Coinflip", value=f"You lost coinflip! - {random_arg}")
            embed.set_footer(text=f"Invoked by {ctx.message.author.name}", icon_url=ctx.message.author.avatar.url)
            await ctx.send(embed=embed)

    else:
        embed.add_field(name="Coinflip", value=f"You don't have enough money!")
        embed.set_footer(text=f"Invoked by {ctx.message.author.name}", icon_url=ctx.message.author.avatar.url)
        await ctx.send(embed=embed)


@client.command()
@is_registered
async def slots(ctx: commands.Context, money: int):
    money_multi = money * 2
    random_slots_data = [None for _ in range(9)]
    i = 0
    for _ in random_slots_data:
        random_slots_data[i] = random.choice([":tada:", ":cookie:", ":large_blue_diamond:",
                                              ":money_with_wings:", ":moneybag:", ":cherries:"])

        i += 1
        if i == len(random_slots_data):
            break
    r = await economy.get_user(ctx.message.author.id)
    embed = discord.Embed(
        colour=discord.Color.from_rgb(244, 182, 89)
    )
    if r.bank >= money:

        embed.add_field(name="Slots", value=f"""{random_slots_data[0]} | {random_slots_data[1]} | {random_slots_data[2]}
                                                {random_slots_data[3]} | {random_slots_data[4]} | {random_slots_data[5]}
                                                {random_slots_data[6]} | {random_slots_data[7]} | {random_slots_data[8]}
                                            """)
        embed.set_footer(text=f"Invoked by {ctx.message.author.name}", icon_url=ctx.message.author.avatar.url)
        await ctx.send(embed=embed)

        if random_slots_data[3] == random_slots_data[4] and random_slots_data[5] == random_slots_data[3]:
            await economy.add_money(ctx.message.author.id, "wallet", money_multi)
            await ctx.send("You won!")
        else:
            await economy.remove_money(ctx.message.author.id, "bank", money)
            await ctx.send("You loss!")

    else:
        embed.add_field(name="Slots", value=f"You don't have enough money!")
        embed.set_footer(text=f"Invoked by {ctx.message.author.name}", icon_url=ctx.message.author.avatar.url)
        await ctx.send(embed=embed)


@client.command()
@is_registered
async def withdraw(ctx: commands.Context, money: int):
    r = await economy.get_user(ctx.message.author.id)
    embed = discord.Embed(
        colour=discord.Color.from_rgb(244, 182, 89)
    )

    if r.bank >= money:
        await economy.add_money(ctx.message.author.id, "wallet", money)
        await economy.remove_money(ctx.message.author.id, "bank", money)

        embed.add_field(name="Withdraw", value=f"Successfully withdrawn {money} money!")
        embed.set_footer(text=f"Invoked by {ctx.message.author.name}", icon_url=ctx.message.author.avatar.url)
        await ctx.send(embed=embed)

    else:

        embed.add_field(name="Withdraw", value=f"You don't have enough money to withdraw!")
        embed.set_footer(text=f"Invoked by {ctx.message.author.name}", icon_url=ctx.message.author.avatar.url)
        await ctx.send(embed=embed)


@client.command()
@is_registered
async def deposit(ctx: commands.Context, money: int):
    r = await economy.get_user(ctx.message.author.id)
    embed = discord.Embed(
        colour=discord.Color.from_rgb(244, 182, 89)
    )

    if r.wallet >= money:
        await economy.add_money(ctx.message.author.id, "bank", money)
        await economy.remove_money(ctx.message.author.id, "wallet", money)

        embed.add_field(name="Deposit", value=f"Successfully deposited {money} money!")
        embed.set_footer(text=f"Invoked by {ctx.message.author.name}", icon_url=ctx.message.author.avatar.url)
        await ctx.send(embed=embed)

    else:

        embed.add_field(name="Deposit", value=f"You don't have enough money to deposit!")
        embed.set_footer(text=f"Invoked by {ctx.message.author.name}", icon_url=ctx.message.author.avatar.url)
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
    embed.set_footer(text=f"Invoked by {ctx.message.author.name}", icon_url=ctx.message.author.avatar.url)
    await ctx.send(embed=embed)


@shop.command()
@is_registered
async def items(ctx: commands.Context):
    embed = discord.Embed(
        colour=discord.Color.from_rgb(244, 182, 89)
    )
    embed.set_author(name="Items")

    for item in items_list["Items"].items():

        if item[1]["available"]:
            embed.add_field(name=item[0].capitalize(), value=f"""Price: **{item[1]['price']}**
                                                                 Description: **{item[1]['description']}**""")

            embed.set_footer(text=f"Invoked by {ctx.author.name}",
                             icon_url=ctx.author.avatar.url)
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

            if item[0] in r.items:
                embed.add_field(name="Error", value=f"You already have that item!")
                embed.set_footer(text=f"Invoked by {ctx.message.author.name}", icon_url=ctx.message.author.avatar.url)
                await ctx.send(embed=embed)

                return

            if r.bank >= item[1]["price"]:
                await economy.add_item(ctx.message.author.id, item[0])
                await economy.remove_money(ctx.message.author.id, "bank", item[1]["price"])

                embed.add_field(name="Success", value=f"Successfully bought **{item[0]}**!")
                embed.set_footer(text=f"Invoked by {ctx.message.author.name}",
                                 icon_url=ctx.message.author.avatar.url)
                await ctx.send(embed=embed)

            else:

                embed.add_field(name="Error", value=f"You don't have enought money to buy this item!")
                embed.set_footer(text=f"Invoked by {ctx.message.author.name}",
                                 icon_url=ctx.message.author.avatar.url)
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

    embed = discord.Embed(
        colour=discord.Color.from_rgb(244, 182, 89)
    )

    if _item in r.items:
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


@client.command()
@is_registered
async def horse_racing(ctx: commands.Context, money: int):
    user = await economy.get_user(ctx.author.id)

    if not user.bank >= money:
        return await ctx.send(content="You don't have enough money to play.")

    author_path = [":horse_racing:", ":blue_square:", ":blue_square:", ":blue_square:", ":blue_square:",
                   ":blue_square:",
                   ":blue_square:", ":blue_square:", ":blue_square:", ":blue_square:", "  :checkered_flag:"]

    enemy_path = [":horse_racing:", ":red_square:", ":red_square:", ":red_square:", ":red_square:", ":red_square:",
                  ":red_square:", ":red_square:", ":red_square:", ":red_square:", "  :checkered_flag:"]

    embed = discord.Embed(
        colour=discord.Color.from_rgb(244, 182, 89)
    )
    embed.set_author(name="Horse race")
    embed.add_field(name="You:", value="".join(author_path), inline=False)
    embed.add_field(name=f"Enemy:", value="".join(enemy_path),
                    inline=False)

    msg = await ctx.send(embed=embed)
    await asyncio.sleep(3)

    author_path[0] = ":blue_square:"
    enemy_path[0] = ":red_square:"

    author_path_update = random.randint(2, 6)
    enemy_path_update = random.randint(2, 6)

    author_path[author_path_update] = ":horse_racing:"
    enemy_path[enemy_path_update] = ":horse_racing:"

    embed.clear_fields()
    embed.add_field(name="You:", value="".join(author_path), inline=False)
    embed.add_field(name=f"Enemy:", value="".join(enemy_path),
                    inline=False)

    await msg.edit(embed=embed)
    await asyncio.sleep(3)

    author_path[author_path_update] = ":blue_square:"
    enemy_path[enemy_path_update] = ":red_square:"

    author_path_update = random.randint(author_path_update, 9)
    enemy_path_update = random.randint(enemy_path_update, 9)

    author_path[author_path_update] = ":horse_racing:"
    enemy_path[enemy_path_update] = ":horse_racing:"

    embed.clear_fields()
    embed.add_field(name="You:", value="".join(author_path), inline=False)
    embed.add_field(name=f"Enemy:", value="".join(enemy_path),
                    inline=False)
    await msg.edit(embed=embed)

    if author_path_update > enemy_path_update:
        await economy.add_money(ctx.author.id, "wallet", money * 2)

        await ctx.send(content="You won!")

    else:
        await economy.remove_money(ctx.author.id, "bank", money)

        await ctx.send(content="You lose!")


asyncio.new_event_loop().run_until_complete(client.start(token=BOT_TOKEN, reconnect=True))
