import sqlite3
from dataclasses import dataclass

@dataclass
class Database_Movies:
    connect: sqlite3.Connection = None
    cursor: sqlite3.Cursor = None

    def __post_init__(self):
        self.connect = sqlite3.connect('movies.db')
        self.cursor = self.connect.cursor()

    def create_table(self):
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS movies(
            id INTEGER PRIMARY KEY,
            movi_code INTEGER NOT NULL,
            movi_name TEXT NOT NULL,
            movi_vd TEXT NOT NULL)
        """)
        self.connect.commit()

    def add_movies(self, movi_code, movi_name, movi_vd):
        self.cursor.execute("INSERT INTO movies (movi_code, movi_name, movi_vd) VALUES (?, ?, ?)", (movi_code, movi_name, movi_vd))
        self.connect.commit()

    def select_movies(self):
        self.cursor.execute("SELECT * FROM movies") 
        return self.cursor.fetchall()

    def get_movie_by_code(self, movi_code):
        self.cursor.execute("SELECT * FROM movies WHERE movi_code = ?", (movi_code,))
        result = self.cursor.fetchone()
        if result:
            return {
                'id': result[0],
                'movi_code': result[1],
                'movi_name': result[2],
                'movi_vd': result[3]
            }
        return None

    def delete_one(self, movie_id):
        self.cursor.execute("DELETE FROM movies WHERE id=?", (movie_id,))
        self.connect.commit()

    def update_movies(self, movie_id, movi_code, movi_name, movi_vd):
        self.cursor.execute("UPDATE movies SET movi_code = ?, movi_name = ?, movi_vd = ? WHERE id = ?",
                            (movi_code, movi_name, movi_vd, movie_id)) 
        self.connect.commit()

    def close(self):
        if self.cursor:
            self.cursor.close()
        if self.connect:
            self.connect.close()
