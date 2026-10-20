import sqlite3
import aiosqlite
import asyncio





class DataBase():
    def __init__(self, filename):
        self.filename = filename
        self.pool = None

    async def connect(self):
        self.pool = await aiosqlite.connect(self.filename)
        await self.pool.commit()

    async def close(self):
        if self.pool:
            await self.pool.close()

    async def update_users(self):
        async with self.pool.execute(f'''UPDATE users SET state = ?''', (0,)):
            await self.pool.commit()

    async def new_user(self, user_id, nickname):
        async with self.pool.execute(f'''INSERT INTO users VALUES("{user_id}", "{nickname}", "0", "0")'''):
            await self.pool.commit()


    async def delete_user(self, user_id):
        async with aiosqlite.connect('tgbot.db') as db:
            await db.execute(f'DELETE FROM users WHERE id = {user_id}')
            await db.commit()


    async def set_score(self, user_id, score):
        print("Устанавливаю счет")
        async with aiosqlite.connect("tgbot.db") as db:
            await db.execute(
                "UPDATE users SET score = score + ? WHERE id = ?", (score, user_id))
            await db.commit()     

    async def get_user(self, user_id):
        async with aiosqlite.connect("tgbot.db") as db:
            async with db.execute(f'''SELECT name, score, state FROM users WHERE id = {user_id}''') as cur:
                name = await cur.fetchone()
                if name:
                    return name
                return None

    async def set_user_status(self, user_id, state):
        async with aiosqlite.connect("tgbot.db") as db:
            await db.execute(f"UPDATE users SET state = {state} WHERE id = {user_id}")
            await db.commit()

    async def get_user_score(self, user_id):
        async with aiosqlite.connect("tgbot.db") as db:
             async with db.execute(f'''SELECT score FROM users WHERE id = {user_id}''') as cur:
                name = await cur.fetchone()
                if name:
                    return name
                return None


    async def get_users_ready_for_battle(self):
        async with aiosqlite.connect("tgbot.db") as db:
                async with db.execute(f'''SELECT name, score, state FROM users WHERE state = ?''', (1, )) as cur:
                    return await cur.fetchall()

    async def get_user_state(self, user_id):
        async with aiosqlite.connect("tgbot.db") as db:
            async with db.execute(f'''SELECT state FROM users WHERE id = ?''', (user_id, )) as cur:
                return await cur.fetchone()

