import asyncio
import random
import typing

import discord
from discord import app_commands

from DiscordEconomy.Sqlite import Economy
# or if you want to use mongodb
# from DiscordEconomy.MongoDB import Economy


# Pass here token as string and guild id where to register slash commands

GUILD_ID = 1234567890
TEST_GUILD = discord.Object(id=GUILD_ID)
BOT_TOKEN = ""
USER_COOLDOWNS = {}



def is_registered():
    async def predicate(interaction: discord.Interaction):
        r = await economy.is_registered(interaction.user.id)
        return r

    return app_commands.check(predicate)


def cooldown(when: typing.Union[int, float]):
    async def __handle_cooldown(when: typing.Union[int, float], interaction: discord.Interaction):
        USER_COOLDOWNS[interaction.user.id] = when
        await asyncio.sleep(when)
        USER_COOLDOWNS.pop(interaction.user.id)

    async def predicate(interaction: discord.Interaction):
        if interaction.user.id in USER_COOLDOWNS:
            raise app_commands.AppCommandError("User is on cooldown")

        asyncio.ensure_future(__handle_cooldown(when, interaction))

        return True

    return app_commands.check(predicate)


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


class DiscordEconomyClient(discord.Client):
    def __init__(self):
        intents = discord.Intents.default()
        intents.members = True

        self.is_synced = False

        super().__init__(intents=intents)

    async def on_ready(self):
        await self.wait_until_ready()

        if not self.is_synced:
            print("Syncing application(/) commands")
            await tree.sync(guild=TEST_GUILD)



class Shop(app_commands.Group):

    @app_commands.command(description="See the list of all available items.")
    @is_registered()
    async def items(self, interaction: discord.Interaction):

        embed = discord.Embed(
            colour=discord.Color.from_rgb(244, 182, 89)
        )
        embed.set_author(name="Items")
        for item in items_list["Items"].items():

            if item[1]["available"]:
                embed.add_field(name=item[0].capitalize(), value=f"""Price: **{item[1]['price']}**
                                                                     Description: **{item[1]['description']}**""")

                embed.set_footer(text=f"Invoked by {interaction.user.name}",
                                 icon_url=interaction.user.avatar.url)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(description="Buy an item!")
    @is_registered()
    async def buy(self, interaction: discord.Interaction, *, item: str):

        _item = item.lower()
        _cache = []
        embed = discord.Embed(
            colour=discord.Color.from_rgb(244, 182, 89)
        )

        for item in items_list["Items"].items():
            if item[0] == _item:
                _cache.append(item[0])

                r = await economy.get_user(interaction.user.id)

                if item[0] in r.items:
                    embed.add_field(name="Error", value=f"You already have that item!")
                    embed.set_footer(text=f"Invoked by {interaction.user.name}",
                                     icon_url=interaction.user.avatar.url)
                    await interaction.response.send_message(embed=embed)

                    return

                if r.bank >= item[1]["price"]:
                    await economy.add_item(interaction.user.id, item[0])
                    await economy.remove_money(interaction.user.id, "bank", item[1]["price"])

                    embed.add_field(name="Success", value=f"Successfully bought **{item[0]}**!")
                    embed.set_footer(text=f"Invoked by {interaction.user.name}",
                                     icon_url=interaction.user.avatar.url)
                    await interaction.response.send_message(embed=embed)

                else:

                    embed.add_field(name="Error", value=f"You don't have enought money to buy this item!")
                    embed.set_footer(text=f"Invoked by {interaction.user.name}",
                                     icon_url=interaction.user.avatar.url)
                    await interaction.response.send_message(embed=embed)
                break

        if len(_cache) <= 0:
            embed.add_field(name="Error", value="Item with that name does not exists!")
            await interaction.response.send_message(embed=embed)

    @app_commands.command(description="Sell an item from your inventory!")
    @is_registered()
    async def sell(self, interaction: discord.Interaction, *, item: str):
        r = await economy.get_user(interaction.user.id)

        _item = item.lower()

        embed = discord.Embed(
            colour=discord.Color.from_rgb(244, 182, 89)
        )

        if _item in r.items:
            for item in items_list["Items"].items():
                if item[0] == _item:
                    item_prc = item[1]["price"] / 2

                    await economy.add_money(interaction.user.id, "bank", item_prc)
                    await economy.remove_item(interaction.user.id, item[0])

                    embed.add_field(name="Success", value=f"Successfully sold **{item[0]}**!")
                    await interaction.response.send_message(embed=embed)
                    break
        else:

            embed.add_field(name="Error", value=f"You don't have this item!")
            await interaction.response.send_message(embed=embed)


client = DiscordEconomyClient()
tree = app_commands.CommandTree(client)

tree.add_command(Shop(), guild=TEST_GUILD)


economy = Economy()
# or if you want to use mongodb
# economy = Economy("mongodb+srv://user:password@clusterIP/Database?retryWrites=true&w=majority", database_name="Discord")


@tree.error
async def on_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    print(USER_COOLDOWNS)
    embed = discord.Embed(
        colour=discord.Color.from_rgb(244, 182, 89)
    )

    embed.add_field(name="Error", value=str(error))
    embed.set_footer(text=f"Invoked by {interaction.user.name}",
                     icon_url=interaction.user.avatar.url)

    await interaction.response.send_message(embed=embed)



@tree.command(guild=TEST_GUILD, description="Check your balance.")
@is_registered()
async def balance(interaction: discord.Interaction, member: discord.Member = None):
    member = member or interaction.user

    await economy.is_registered(member.id)

    user_account = await economy.get_user(member.id)

    embed = discord.Embed(
        colour=discord.Color.from_rgb(244, 182, 89)
    )
    embed.add_field(name=f"{member.display_name}'s balance", value=f"""Bank: **{user_account.bank}**
                                                                     Wallet: **{user_account.wallet}**
                                                                     Items: **{', '.join(user_account.items)}**""")

    embed.set_footer(text=f"Invoked by {interaction.user.name}",
                     icon_url=interaction.user.avatar.url)
    await interaction.response.send_message(embed=embed)



@tree.command(guild=TEST_GUILD, description="Receive daily reward for some money.")
@is_registered()
@cooldown(60)
async def reward(interaction: discord.Interaction):
    random_amount = random.randint(50, 150)
    await economy.add_money(interaction.user.id, "wallet", random_amount)

    embed = discord.Embed(
        colour=discord.Color.from_rgb(244, 182, 89)
    )
    embed.add_field(name=f"Reward", value=f"Successfully claimed reward!")
    embed.set_footer(text=f"Invoked by {interaction.user.name}",
                     icon_url=interaction.user.avatar.url)
    await interaction.response.send_message(embed=embed)


@tree.command(guild=TEST_GUILD, description="Toss a coin.")
@is_registered()
async def coinflip(interaction: discord.Interaction, money: int, side: str):
    side = side.lower()
    random_arg = random.choice(["tails", "heads"])

    r = await economy.get_user(interaction.user.id)
    embed = discord.Embed(
        colour=discord.Color.from_rgb(244, 182, 89)
    )

    if r.bank >= money:
        if side == random_arg:
            await economy.add_money(interaction.user.id, "wallet", money * 2)

            embed.add_field(name="Coinflip", value=f"You won coinflip! - {random_arg}")
            embed.set_footer(text=f"Invoked by {interaction.user.name}",
                             icon_url=interaction.user.avatar.url)
            await interaction.response.send_message(embed=embed)
        else:
            await economy.remove_money(interaction.user.id, "wallet", money)

            embed.add_field(name="Coinflip", value=f"You lost coinflip! - {random_arg}")
            embed.set_footer(text=f"Invoked by {interaction.user.name}",
                             icon_url=interaction.user.avatar.url)
            await interaction.response.send_message(embed=embed)

    else:
        embed.add_field(name="Coinflip", value=f"You don't have enough money!")
        embed.set_footer(text=f"Invoked by {interaction.user.name}",
                         icon_url=interaction.user.avatar.url)
        await interaction.response.send_message(embed=embed)


@tree.command(guild=TEST_GUILD, description="Play some slots.")
@is_registered()
async def slots(interaction: discord.Interaction, money: int):
    random_slots_data = [None for _ in range(9)]
    i = 0
    for _ in random_slots_data:
        random_slots_data[i] = random.choice([":tada:", ":cookie:", ":large_blue_diamond:",
                                              ":money_with_wings:", ":moneybag:", ":cherries:"])

        i += 1
        if i == len(random_slots_data):
            break

    r = await economy.get_user(interaction.user.id)

    embed = discord.Embed(
        colour=discord.Color.from_rgb(244, 182, 89)
    )

    if r.bank >= money:

        embed.add_field(name="Slots", value=f"""{random_slots_data[0]} | {random_slots_data[1]} | {random_slots_data[2]}
                                                {random_slots_data[3]} | {random_slots_data[4]} | {random_slots_data[5]}
                                                {random_slots_data[6]} | {random_slots_data[7]} | {random_slots_data[8]}
                                            """)
        embed.set_footer(text=f"Invoked by {interaction.user.name}",
                         icon_url=interaction.user.avatar.url)
        await interaction.response.send_message(embed=embed)

        if random_slots_data[3] == random_slots_data[4] and random_slots_data[5] == random_slots_data[3]:
            await economy.add_money(interaction.user.id, "wallet", money * 2)
            await interaction.followup.send(content="You won!")

        else:
            await economy.remove_money(interaction.user.id, "bank", money)
            await interaction.followup.send(content="You lose!")

    else:
        embed.add_field(name="Slots", value=f"You don't have enough money!")
        embed.set_footer(text=f"Invoked by {interaction.user.name}",
                         icon_url=interaction.user.avatar.url)
        await interaction.response.send_message(embed=embed)


@tree.command(guild=TEST_GUILD, description="Withdraw money from your account.")
@is_registered()
async def withdraw(interaction: discord.Interaction, money: int):
    r = await economy.get_user(interaction.user.id)

    embed = discord.Embed(
        colour=discord.Color.from_rgb(244, 182, 89)
    )

    if r.bank >= money:
        await economy.add_money(interaction.user.id, "wallet", money)
        await economy.remove_money(interaction.user.id, "bank", money)

        embed.add_field(name="Withdraw", value=f"Successfully withdrawn {money} money!")
        embed.set_footer(text=f"Invoked by {interaction.user.name}",
                         icon_url=interaction.user.avatar.url)
        await interaction.response.send_message(embed=embed)

    else:

        embed.add_field(name="Withdraw", value=f"You don't have enough money to withdraw!")
        embed.set_footer(text=f"Invoked by {interaction.user.name}",
                         icon_url=interaction.user.avatar.url)
        await interaction.response.send_message(embed=embed)


@tree.command(guild=TEST_GUILD, description="Deposit to your account.")
@is_registered()
async def deposit(interaction: discord.Interaction, money: int):
    r = await economy.get_user(interaction.user.id)

    embed = discord.Embed(
        colour=discord.Color.from_rgb(244, 182, 89)
    )

    if not r.wallet >= money:
        embed.add_field(name="Deposit", value=f"You don't have enough money to deposit!")
        embed.set_footer(text=f"Invoked by {interaction.user.name}",
                         icon_url=interaction.user.avatar.url)
        return await interaction.response.send_message(embed=embed)

    await economy.add_money(interaction.user.id, "bank", money)
    await economy.remove_money(interaction.user.id, "wallet", money)

    embed.add_field(name="Deposit", value=f"Successfully deposited {money} money!")
    embed.set_footer(text=f"Invoked by {interaction.user.name}",
                     icon_url=interaction.user.avatar.url)
    await interaction.response.send_message(embed=embed)


@tree.command(guild=TEST_GUILD, description="Play some horse racing.")
@is_registered()
async def horse_racing(interaction: discord.Interaction, money: int):
    user = await economy.get_user(interaction.user.id)

    if not user.bank >= money:
        return await interaction.response.send_message(content="You don't have enough money to play.")

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

    await interaction.response.send_message(embed=embed)
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

    await interaction.edit_original_message(embed=embed)
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
    await interaction.edit_original_message(embed=embed)

    if author_path_update > enemy_path_update:
        await economy.add_money(interaction.user.id, "wallet", money * 2)

        await interaction.followup.send(content="You won!")

    else:
        await economy.remove_money(interaction.user.id, "bank", money)

        await interaction.followup.send(content="You lose!")


asyncio.new_event_loop().run_until_complete(client.start(token=BOT_TOKEN, reconnect=True))
