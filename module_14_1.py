import sqlite3

connection = sqlite3.connect("not_telegram.db")
cursor = connection.cursor()

cursor.execute('''CREATE TABLE IF NOT EXISTS Users (
id INTEGER PRIMARY KEY,
username TEXT NOT NULL,
email TEXT NOT NULL,
age INTEGER,
balance INTEGER NOT NULL
)''')

for i in range(1,11):
    cursor.execute("INSERT INTO Users (username, email, age, balance) VALUES (?, ?, ?, ?)",
                   ("User{}".format(i), "User{}@example.com".format(i), i*10, 1000))

for i in range(1, 11, 2):
    cursor.execute("UPDATE Users SET balance = ? WHERE id = ?", (500, i))

for i in range(1, 11, 3):
    cursor.execute("DELETE FROM Users WHERE id = ?", (i,))

cursor.execute("SELECT username, email, age, balance FROM Users WHERE age != 60")
selected_users = cursor.fetchall()
for sl_usr in selected_users:
    print("Имя:", sl_usr[0], "| Email:", sl_usr[1], "| Возраст:", sl_usr[2], "| Баланс:", sl_usr[3], )

connection.commit()
connection.close()
