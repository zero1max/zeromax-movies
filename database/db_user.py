import sqlite3
from dataclasses import dataclass

@dataclass
class Database_Users:
    connect: sqlite3.Connection = None
    cursor: sqlite3.Cursor = None

    def __post_init__(self):
        self.connect = sqlite3.connect('users.db')
        self.cursor = self.connect.cursor()

    def create_table(self):
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY,
            user_id INTEGER NOT NULL,
            full_name TEXT NOT NULL,
            surname TEXT NOT NULL
        )''')
        self.connect.commit()

    def add_user(self, user_id, full_name, surname):
        self.cursor.execute("INSERT INTO users (user_id, full_name, surname) VALUES (?, ?, ?)", (user_id, full_name, surname))
        self.connect.commit()

    def select_users(self):
        self.cursor.execute("SELECT * FROM users") 
        return self.cursor.fetchall()

    def select_user(self,id):
        self.cursor.execute("SELECT * FROM users WHERE id = ?",(id,)) 
        return self.cursor.fetchone()
    
    def delete_one(self, user_id, value):
        self.cursor.execute(f"DELETE FROM users WHERE {user_id}=?",(value,))
        self.connect.commit()

    def update_product(self,id,user_id,full_name,surname):
        self.cursor.execute("UPDATE users SET user_id = ?, full_name = ?, surname = ? WHERE id = ?",
                            (user_id,full_name,surname)
                            ) 
        self.connect.commit()

    def close(self):
        if self.cursor:
            self.cursor.close()
        if self.connect:
            self.connect.close()