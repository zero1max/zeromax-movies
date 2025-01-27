import aiosqlite

DATABASE = 'movies.db'

async def setup_movie():
    async with aiosqlite.connect(DATABASE) as db:
        await db.execute("""CREATE TABLE IF NOT EXISTS movies(
            id INTEGER PRIMARY KEY,
            movi_code INTEGER NOT NULL,
            movi_name TEXT NOT NULL,
            movi_vd TEXT NOT NULL)
        """)
        await db.commit()

async def add_movie(movi_code, movi_name, movi_vd):
    async with aiosqlite.connect(DATABASE) as db:
        await db.execute("INSERT INTO movies (movi_code, movi_name, movi_vd) VALUES (?, ?, ?)", (movi_code, movi_name, movi_vd))
        await db.commit()

async def select_movies():
    async with aiosqlite.connect(DATABASE) as db:
        cursor = await db.execute("SELECT * FROM movies")
        return await cursor.fetchall()
    
async def get_movie_by_code(movi_code):
    async with aiosqlite.connect(DATABASE) as db:
        cursor = await db.execute("SELECT * FROM movies WHERE movi_code = ?", (movi_code,))
        row = await cursor.fetchone()
        if row:
            return {
                'id': row[0],
                'movi_code': row[1],
                'movi_name': row[2],
                'movi_vd': row[3]
            }
        return None
    
async def delete_movie(movie_id):
    async with aiosqlite.connect(DATABASE) as db:
        await db.execute("DELETE FROM movies WHERE id=?", (movie_id,))
        await db.commit()

async def update_movie(movie_id, movi_code, movi_name, movi_vd):
    async with aiosqlite.connect(DATABASE) as db:
        await db.execute("UPDATE movies SET movi_code = ?, movi_name = ?, movi_vd = ? WHERE id = ?",
                         (movi_code, movi_name, movi_vd, movie_id))
        await db.commit()

