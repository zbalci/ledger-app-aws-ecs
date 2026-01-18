import mysql.connector
import os


def connect():
    config = {
      'user': os.getenv("DATABASE_USER"),
      'password': os.getenv("DATABASE_PASS"),
      'host': os.getenv("DATABASE_HOST"),
      'port': int(os.getenv("DATABASE_HOST_PORT")),
      'database': os.getenv("DATABASE"),
      'raise_on_warnings': True
    }

    cnx = mysql.connector.connect(**config)
    return cnx


def get():
    cnx = connect()
    result_list = []
    if cnx and cnx.is_connected():
        with cnx.cursor(buffered=True) as cursor:
            cursor.execute("SELECT * FROM transactions")
            result = cursor.fetchall()
            for row in result:
                result_list.append({"id": row[0], "date": row[1], "amount": row[2]})
    cnx.close()
    return result_list


def add(date, amount):
    cnx = connect()
    if cnx and cnx.is_connected():
        with cnx.cursor(buffered=True) as cursor:
            cursor.execute(f'''insert into transactions (date, amount) values ("{date}", {amount})''')
            cnx.commit()


def edit(id, date, amount):
    cnx = connect()
    if cnx and cnx.is_connected():
        with cnx.cursor(buffered=True) as cursor:
            cursor.execute(f'''UPDATE transactions SET date="{date}", amount={amount} WHERE id={id}''')
            cnx.commit()


def delete(id):
    cnx = connect()
    if cnx and cnx.is_connected():
        with cnx.cursor(buffered=True) as cursor:
            cursor.execute(f'''DELETE from transactions WHERE id={id}''')
            cnx.commit()


def search(amount1, amount2):
    cnx = connect()
    result_list = []
    if cnx and cnx.is_connected():
        with cnx.cursor(buffered=True) as cursor:
            cursor.execute(f"SELECT * FROM transactions WHERE amount BETWEEN {amount1} AND {amount2};")
            result = cursor.fetchall()
            for row in result:
                result_list.append({"id": row[0], "date": row[1], "amount": row[2]})
        cnx.close()
        return result_list
