import sqlite3


class Economy:
    def __init__(self):
        conn = sqlite3.connect("database.db")
        c = conn.cursor()
        self.conn = conn
        self.c = c
        self.c.execute("CREATE TABLE IF NOT EXISTS economy(id integer, bank integer, wallet integer, items text)")

    async def is_registered(self, user_id):
        query = self.c.execute("SELECT * FROM economy WHERE id = ?", (user_id,)).fetchone()
        if not query:
            self.c.execute(f"INSERT INTO economy VALUES({user_id}, 0, 0, 'None')")
        self.conn.commit()
        return True

    async def get_user(self, user_id):
        r = self.c.execute("SELECT * FROM economy WHERE id = ?", (user_id,)).fetchone()

        return r

    async def delete_user_account(self, user_id):
        self.c.execute("DELETE FROM economy WHERE id = ?", (user_id,))
        self.conn.commit()

        return True

    async def get_all_data(self):
        r = self.c.execute("SELECT * FROM economy").fetchall()

        return r

    async def add_money(self, user_id, value, amount):
        user_account = self.c.execute(f"SELECT {value} FROM economy WHERE id = ?", (user_id,)).fetchone()
        user_account = user_account[0]

        money = user_account + amount

        self.c.execute(f"UPDATE economy SET {value} = ? WHERE id = ?", (money, user_id,))
        self.conn.commit()

        return True

    async def remove_money(self, user_id, value, amount):
        user_account = self.c.execute(f"SELECT {value} FROM economy WHERE id = ?", (user_id,)).fetchone()
        user_account = user_account[0]

        money = user_account - amount

        self.c.execute(f"UPDATE economy SET {value} = ? WHERE id = ?", (money, user_id,))
        self.conn.commit()

        return True

    async def set_money(self, user_id, value, amount):
        self.c.execute(f"UPDATE economy SET {value} = ? WHERE id = ?", (amount, user_id,))
        self.conn.commit()

        return True

    async def add_item(self, user_id, item):
        r = self.c.execute("SELECT items FROM economy WHERE id = ?", (user_id,)).fetchone()
        your_items = r[0]
        your_items = your_items.split(" | ")
        if item in your_items:
            return "You already have this item!"
        your_items.append(item)
        your_items = str.join(" | ", your_items)
        your_items = your_items.replace("None | ", "")
        self.c.execute("UPDATE economy SET items = ? WHERE id = ?", (your_items, user_id))
        self.conn.commit()

        return True

    async def remove_item(self, user_id, item):
        r = self.c.execute("SELECT items FROM economy WHERE id = ?", (user_id,)).fetchone()
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
            self.c.execute("UPDATE economy SET items = ? WHERE id = ?", (your_items, user_id))
            self.conn.commit()
            return True

        else:
            return "You don't have this item!"
