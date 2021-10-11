import asyncio
import aiosqlite

from .exceptions import (NoItemFound, ItemAlreadyExists)


async def is_table_exists():
    con = await aiosqlite.connect("database.db")
    c = await con.cursor()

    await c.execute("CREATE TABLE IF NOT EXISTS economy(id integer, bank integer, wallet integer, items text)")

    await con.commit()
    await con.close()


class Economy:
    def __init__(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(is_table_exists())

    async def is_registered(self, user_id):

        con = await aiosqlite.connect("database.db")
        c = await con.cursor()

        query = await c.execute("SELECT * FROM economy WHERE id = ?", (user_id,))
        query = await query.fetchone()

        if not query:
            await c.execute(f"INSERT INTO economy VALUES(?, 0, 0, 'None')", (user_id,))

        await con.commit()
        await con.close()

        return True

    async def get_user(self, user_id):

        con = await aiosqlite.connect("database.db")
        c = await con.cursor()

        r = await c.execute("SELECT * FROM economy WHERE id = ?", (user_id,))
        r = await r.fetchone()

        await con.close()

        return r

    async def delete_user_account(self, user_id):

        con = await aiosqlite.connect("database.db")
        c = await con.cursor()

        await c.execute("DELETE FROM economy WHERE id = ?", (user_id,))

        await con.commit()
        await con.close()

        return True

    async def get_all_data(self):

        con = await aiosqlite.connect("database.db")
        c = await con.cursor()

        r = await c.execute("SELECT * FROM economy")
        r = await r.fetchall()

        await con.close()

        return r

    async def add_money(self, user_id, value, amount):

        con = await aiosqlite.connect("database.db")
        c = await con.cursor()

        user_account = await c.execute(f"SELECT {value} FROM economy WHERE id = ?", (user_id,))
        user_account = await user_account.fetchone()
        user_account = user_account[0]

        money = user_account + amount

        await c.execute(f"UPDATE economy SET {value} = ? WHERE id = ?", (money, user_id,))

        await con.commit()
        await con.close()

        return True

    async def remove_money(self, user_id, value, amount):

        con = await aiosqlite.connect("database.db")
        c = await con.cursor()

        user_account = await c.execute(f"SELECT {value} FROM economy WHERE id = ?", (user_id,))
        user_account = await user_account.fetchone()
        user_account = user_account[0]

        money = user_account - amount

        await c.execute(f"UPDATE economy SET {value} = ? WHERE id = ?", (money, user_id,))

        await con.commit()
        await con.close()

        return True

    async def set_money(self, user_id, value, amount):

        con = await aiosqlite.connect("database.db")
        c = await con.cursor()

        await c.execute(f"UPDATE economy SET {value} = ? WHERE id = ?", (amount, user_id,))

        await con.commit()
        await con.close()

        return True

    async def add_item(self, user_id, item):

        con = await aiosqlite.connect("database.db")
        c = await con.cursor()

        r = await c.execute("SELECT items FROM economy WHERE id = ?", (user_id,))
        r = await r.fetchone()

        your_items = r[0]
        your_items = your_items.split(" | ")

        if item in your_items:
            raise ItemAlreadyExists("You already have this item!")

        your_items.append(item)
        your_items = str.join(" | ", your_items)
        your_items = your_items.replace("None | ", "")

        await c.execute("UPDATE economy SET items = ? WHERE id = ?", (your_items, user_id))

        await con.commit()
        await con.close()

        return True

    async def remove_item(self, user_id, item):

        con = await aiosqlite.connect("database.db")
        c = await con.cursor()

        r = await c.execute("SELECT items FROM economy WHERE id = ?", (user_id,))
        r = await r.fetchone()

        your_items = r[0]
        your_items_list = your_items.split(" | ")

        if item in your_items_list:
            if your_items.endswith(item):
                your_items = your_items + " |"

            if your_items.startswith(item):
                your_items = "| " + your_items

            your_items = your_items.replace("| " + item + " |", "")

            if your_items.startswith(" "):
                your_items = your_items[1:]

            await c.execute("UPDATE economy SET items = ? WHERE id = ?", (your_items, user_id))

            await con.commit()
            await con.close()

            return True

        else:
            raise NoItemFound("You don't have this item!")
