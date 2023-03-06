import sqlite3
from PyQt5.QtSql import QSqlDatabase, QSqlQuery

# Создание подключения к базе данных SQLite
conn = sqlite3.connect('data.db')

# Создание таблицы
c = conn.cursor()
c.execute('''CREATE TABLE acfts
             (id INTEGER PRIMARY KEY,
              ACFT_ID TEXT,
              EMPTY_WEIGHT INTEGER,
              EMPTY_CG INTEGER,
              EQUIPED_WEIGHT INTEGER,
              EQUIPED_CG INTEGER)''')
conn.commit()

# Инициализация объекта базы данных Qt
db = QSqlDatabase.addDatabase('QSQLITE')
db.setDatabaseName('example.db')

# Проверка подключения к базе данных
if db.open():
    print('База данных открыта успешно')
else:
    print('Ошибка открытия базы данных')
