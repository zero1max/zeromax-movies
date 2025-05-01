import aiosqlite

DATABASE = 'users.db'

async def setup_user():
    async with aiosqlite.connect(DATABASE) as db:
        await db.execute('''CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY,
            user_id INTEGER NOT NULL,
            full_name TEXT NOT NULL,
            username TEXT NOT NULL UNIQUE
        )''')


async def add_user(user_id: int, full_name: str, username: str):
    async with aiosqlite.connect(DATABASE) as db:
        # Avval mavjud foydalanuvchini tekshiramiz
        cursor = await db.execute("SELECT 1 FROM users WHERE username = ?", (username,))
        user_exists = await cursor.fetchone()

        if not user_exists:
            await db.execute(
                "INSERT INTO users (user_id, full_name, username) VALUES (?, ?, ?)",
                (user_id, full_name, username)
            )
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

async def update_user(id, user_id, full_name, username):
    async with aiosqlite.connect(DATABASE) as db:
        await db.execute("UPDATE users SET user_id = ?, full_name = ?, username = ? WHERE id = ?",
                         (user_id, full_name, username, id))
        await db.commit()
