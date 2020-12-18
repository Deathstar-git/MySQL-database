from random import randint
from datetime import datetime
import pymysql
import funkybob
import re

connection = pymysql.connect(host='localhost',
                             user='root',
                             password='MYSQL79025t',
                             db='custom_products',
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)
cursor = connection.cursor()


def iter_row(cur, size=10):
    while True:
        rows = cur.fetchmany(size)
        if not rows:
            break
        for row in rows:
            yield row


def get_random_phone(length):
    charset = "1234567890"
    result = '8'
    for i in range(1, length):
        result += charset[randint(0, len(charset) - 1)]
    return result


def get_random_good(length):
    charset = "acbdefghijklmnopqrstuvxz"
    result = ''
    for i in range(0, length):
        result += charset[randint(0, len(charset) - 1)]
    return result


def create_tables():
    # создание таблицы Users
    cursor.execute("CREATE TABLE IF NOT EXISTS Users("
                   "id INT PRIMARY KEY AUTO_INCREMENT,"
                   "name VARCHAR(20),"
                   "surname VARCHAR(20),"
                   "phone VARCHAR(11),"
                   "order_price INT DEFAULT 0)")

    # создание таблицы Orders
    cursor.execute("CREATE TABLE IF NOT EXISTS Orders("
                   "order_id INT PRIMARY KEY AUTO_INCREMENT,"
                   "date DATETIME DEFAULT 0 NOT NULL,"
                   "time VARCHAR(20) DEFAULT 0 NOT NULL,"
                   "order_price INT DEFAULT 0 NOT NULL,"
                   "user_id INT)")

    # создание таблицы Goods
    cursor.execute("CREATE TABLE IF NOT EXISTS Goods("
                   "good_id INT PRIMARY KEY AUTO_INCREMENT,"
                   "name VARCHAR(10),"
                   "price INT DEFAULT 0 NOT NULL,"
                   "remained INT DEFAULT 0 NOT NULL,"
                   "with_discount VARCHAR(3))")

    # создание таблицы Order_rows
    cursor.execute("CREATE TABLE IF NOT EXISTS Order_rows("
                   "id INT PRIMARY KEY AUTO_INCREMENT,"
                   "id_good INT,"
                   "id_order INT,"
                   "piece INT,"
                   "CONSTRAINT order_row_fk_1 FOREIGN KEY(id_good) REFERENCES Goods(good_id) "
                   "ON DELETE CASCADE ON UPDATE CASCADE,"
                   "CONSTRAINT order_row_fk_2 FOREIGN KEY(id_order) REFERENCES Orders(order_id) "
                   "ON DELETE CASCADE ON UPDATE CASCADE)")

    # привязка связанных ключей
    cursor.execute("ALTER TABLE Orders "
                   "ADD "
                   "CONSTRAINT order_fk_1 FOREIGN KEY(user_id) REFERENCES Users(id) "
                   "ON DELETE CASCADE ON UPDATE CASCADE")
    # # вывод таблицы
    # cursor.execute("SELECT * FROM Users")
    # for row_data in iter_row(cursor, 10):
    #     print(row_data)


def fill_tables():
    # запрос для заполнения таблицы Users
    for i in range(1, 1000):
        generator = funkybob.UniqueRandomNameGenerator()
        string = re.split('_', generator[0])
        val = (string[1], string[0], get_random_phone(10))
        query = "INSERT INTO Users (name, surname, phone) VALUES (%s, %s, %s)"
        cursor.execute(query, val)

    # # запрос для заполнения таблицы Orders
    # for i in range(1, 1000):
    #     t = time.time()
    #     d = datetime.datetime.now()
    #     val = (d, t, randint(100, 100000))
    #     query = "INSERT INTO Orders (date, time, order_price) VALUES ( %s, %s, %s)"
    #     cursor.execute(query, val)

    # запрос для заполнения таблицы Goods
    for i in range(1, 1000):
        name = get_random_good(10)
        remained = randint(0, 100)
        price = randint(100, 5000)
        r = randint(0, 1)
        if r == 1:
            with_discount = 'yes'
        else:
            with_discount = 'no'
        val = (name, price, remained, with_discount)
        query = "INSERT INTO Goods (name, price, remained, with_discount) VALUES ( %s, %s, %s, %s)"
        cursor.execute(query, val)

    # cохранение изменений
    connection.commit()

    # обновление значений вторичных ключей
    # for i in range(1, 1000):
    #     qe = "SELECT * FROM Users WHERE id = " + str(i)
    #     cursor.execute(qe)
    #     result = cursor.fetchone()
    #     last_id = result['id']
    #     val = (last_id, i)
    #     q = "UPDATE Orders SET `user_id` = %s WHERE order_id = %s"
    #     cursor.execute(q, val)
    #
    # for i in range(1, 1000):
    #     qe = "SELECT * FROM Orders WHERE order_id = " + str(i)
    #     cursor.execute(qe)
    #     result = cursor.fetchone()
    #     price = result['order_price']
    #     val = (price, i)
    #     q = "UPDATE Users SET `order_price` = %s WHERE id = %s"
    #     cursor.execute(q, val)

    # cохранение изменений
    connection.commit()


def show_users():
    print("20 случайных пользователей:")
    query = "SELECT * FROM Users ORDER BY RAND() LIMIT 20"
    cursor.execute(query)
    users = cursor.fetchall()
    for user in users:
        print("id:", user['id'],
              ",Имя:", user['name'],
              ",Фамилия:",
              user['surname'],
              ",Телефон:",
              user['phone'])


def show_goods():
    print("20 случайных товаров:")
    query = "SELECT * FROM Goods ORDER BY RAND() LIMIT 20"
    cursor.execute(query)
    goods = cursor.fetchall()
    for good in goods:
        print("id:", good['good_id'],
              ",Название:", good['name'],
              ",Цена:",
              good['price'],
              ",Осталось шт.:",
              good['remained'],
              ",Cо скидкой:",
              good['with_discount'])


def create_order():
    print("Сделать заказ:")
    d = datetime.now().strftime('%Y-%m-%d')
    t = datetime.now().strftime('%H:%M:%S')
    print("Введите id товара:")
    g_id = input()
    if int(g_id) > 1000:
        print('Такого товара не существует')
        print("Введите id товара:")
        g_id = input()
    good_query = "SELECT price, remained FROM Goods WHERE good_id = " + g_id
    cursor.execute(good_query)
    good = cursor.fetchone()
    rem = good['remained']
    g_price = good['price']

    print("Осталось " + str(rem) + "шт. товара. Сколько хотите заказать?")
    count = int(input())
    if count > int(rem):
        print("Простите,такого кол.ва товара нет в наличии")
        print("Сколько хотите заказать?")
        count = int(input())
    final_price = g_price * count

    print("Введите ваш id:")
    u_id = int(input())
    if u_id > 1000:
        print('Такого пользователя не существует')
        print("Введите ваш id:")
        u_id = int(input())

    order_val = (d, t, final_price, u_id)
    order_query = "INSERT INTO Orders (date, time, order_price, user_id)" \
                  " VALUES ( %s, %s, %s, %s)"
    cursor.execute(order_query, order_val)
    l_id = cursor.lastrowid
    order_row_val = (g_id, l_id, count)
    order_row_query = "INSERT INTO Order_rows (id_good, id_order, piece)" \
                      " VALUES (%s, %s, %s)"
    cursor.execute(order_row_query, order_row_val)

    # сохраняем изменения
    connection.commit()
    print("Заказ успешно добавлен:")
    print("Сумма заказа:", final_price)


# create_tables()
# fill_tables()
show_users()
show_goods()
create_order()
