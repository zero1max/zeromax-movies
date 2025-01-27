import aiosqlite

DATABASE = 'users.db'

async def setup_user():
    async with aiosqlite.connect(DATABASE) as db:
        await db.execute('''CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY,
            user_id INTEGER NOT NULL,
            full_name TEXT NOT NULL,
            surname TEXT NOT NULL
        )''')
        await db.commit()

async def add_user(user_id, full_name, surname):
    async with aiosqlite.connect(DATABASE) as db:
        await db.execute("INSERT INTO users (user_id, full_name, surname) VALUES (?, ?, ?)", (user_id, full_name, surname))
        await db.commit()

async def select_users():
    async with aiosqlite.connect(DATABASE) as db:
        cursor = await db.execute("SELECT * FROM users")
        return await cursor.fetchall()
    
async def select_user(id):
    async with aiosqlite.connect(DATABASE) as db:
        cursor = await db.execute("SELECT * FROM users WHERE id = ?", (id,))
        return await cursor.fetchone()
    
async def delete_one(user_id, value):
    async with aiosqlite.connect(DATABASE) as db:
        await db.execute(f"DELETE FROM users WHERE {user_id}=?", (value,))
        await db.commit()

async def update_user(id, user_id, full_name, surname):
    async with aiosqlite.connect(DATABASE) as db:
        await db.execute("UPDATE users SET user_id = ?, full_name = ?, surname = ? WHERE id = ?",
                         (user_id, full_name, surname, id))
        await db.commit()