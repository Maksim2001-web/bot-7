import sqlite3


# создаем таблицу Products, если она ещё не существует
def initiate_db(db_name="products.db"):
    connect = sqlite3.connect(db_name)
    cursor = connect.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            price INTEGER NOT NULL,
            img TEXT
        )
    """)
    connect.commit()
    connect.close()



# возвращает все записи из таблицы Products
def get_all_products(db_name="products.db"):
    connect = sqlite3.connect(db_name)
    cursor = connect.cursor()
    cursor.execute("SELECT * FROM Products")
    products = cursor.fetchall() # возвращает все записи
    connect.close()
    return products # список записей (каждая запись — кортеж)


# добавление записей в таблицу Products
def add_product(title, description, price, img, db_name="products.db"):
    connect = sqlite3.connect(db_name)
    cursor = connect.cursor()
    cursor.execute("""
        INSERT INTO Products (title, description, price, img)
        VALUES (?, ?, ?, ?)
    """, (title, description, price, img))
    connect.commit() # фиксируем изменения в базе данных
    connect.close()


# удаление таблицы Products, если она существует.
def delete_products_table(db_name="products.db"):
    connect = sqlite3.connect(db_name)
    cursor = connect.cursor()
    cursor.execute("DROP TABLE IF EXISTS Products")
    connect.commit()
    connect.close()
    print("Таблица Products обновлена.")

