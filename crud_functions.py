import sqlite3


def initiate_db():
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS Products (
        id INTEGER PRIMARY KEY,
        title text NOT NULL,
        description text,
        price int NOT NULL
        )
        ''')
    conn.commit()
    conn.close()


def get_all_products():
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()
    cur.execute("SELECT * FROM Products")
    stuff = cur.fetchall()
    conn.close()
    return stuff


def check_add_product():
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()
    cur.execute('SELECT COUNT (*) FROM Products')
    count = cur.fetchone()
    if count[0] == 0:
        for i in range(1, 5):
            cur.execute("INSERT INTO Products(title, description, price) VALUES (?, ?, ?)",
                        ("{}".format(i),
                         "Описание {}".format(i),
                         "{}".format((i * 100) / 5)))
    conn.commit()
    conn.close()
