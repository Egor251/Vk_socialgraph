import sqlite3
import os
from utils import Utils
from tqdm import tqdm
from graph_tools import GraphTools


class DB:

    targetid = ''  # id пользователя, для которого строится граф


    def create_db(self, roundy, typy='normal'):
        if not os.path.exists('db'):
            os.mkdir('db')

        conn = sqlite3.connect(f'db/{self.targetid}.db')  # или :memory: чтобы сохранить в RAM
        cursor = conn.cursor()
        if typy == 'normal':  # для обычного профиля создаём только один тип таблиц
            # cursor.execute("""CREATE TABLE IF NOT EXISTS target(userid INT PRIMARY KEY, first_name TEXT, last_name TEXT, sex INT, city TEXT, country TEXT, birth_date TEXT, company TEXT, position TEXT, university TEXT, faculty TEXT, graduation INT, education_status TEXT, home_town TEXT, is_closed INT); """)
            for i in range(roundy + 1):
                cursor.execute(f"""CREATE TABLE IF NOT EXISTS round{i} (
                   ID INT, baseid INT, friendid INT, is_closed INT);
                """)
            conn.commit()
        elif typy == 'hidden':  # для скрытого профиля создаём три типа таблиц
            for i in range(5):
                # в эту таблицу вносятся попытки найти целевого пользователя
                cursor.execute(f"""CREATE TABLE IF NOT EXISTS attempt{i} (  
                   ID INT, baseid INT, friendid INT, is_closed INT);
                """)
            for i in range(roundy + 1):
                cursor.execute(f"""CREATE TABLE IF NOT EXISTS round{i} (
                   ID INT, baseid INT, friendid INT, is_closed INT);
                """)
            cursor.execute(f"""CREATE TABLE IF NOT EXISTS result (
                           baseid INT, friendid INT, is_closed INT);
                        """)
            conn.commit()
        else:
            assert False, "Как можно умудриться принудительно в коде ввести не тот ключ?"

    # вносит записи в базу (снова очевидно же..)
    def insert_db(self, value, roundy, name='round'):

        def just_id(value, roundy, name):
            try:
                if isinstance(value[0], list):
                    for val in value:
                        cursor.executemany(f"INSERT INTO {name + str(roundy)} VALUES (?,?,?,?)", (val,))
            except IndexError:
                pass

        conn = sqlite3.connect(f'db/{self.targetid}.db')
        cursor = conn.cursor()
        just_id(value, roundy, name)
        conn.commit()

        # Из готовой базы ищет пересечения

    def get_connections_from_db(self, roundy, type='normal'):
        conn = sqlite3.connect(f'db/{self.targetid}.db')
        cursor = conn.cursor()
        total = []
        if type == 'normal':
            total += cursor.execute(f'select baseid, friendid from round0')
            for i in tqdm(range(1, roundy + 1)):
                cursor.execute(f'select baseid, friendid from round{i - 1}')
                a = GraphTools().graph_data_preparation(cursor.fetchall())
                b = []
                for j in tqdm(a):
                    sql = f'select baseid, friendid from round{i} where friendid = {j[1]}'
                    cursor.execute(sql)
                    b += GraphTools().graph_data_preparation(cursor.fetchall())
                print(len(b))
                total += b
        elif type == 'hidden':
            total += cursor.execute(f'select baseid, friendid from result')
            tmp = []
            b = []
            for i in tqdm(range(0, roundy + 1)):
                cursor.execute(f'select baseid, friendid from round{i} where friendid = {total[0][0]}')
                a = cursor.fetchall()
                tmp += a
                b = []
                for j in tqdm(tmp):
                    cursor.execute(f'select baseid, friendid from round{i} where friendid = {j[1]}')
                    b += GraphTools().graph_data_preparation(cursor.fetchall())
            total += GraphTools().graph_data_preparation(tmp)
            total += b
        else:
            assert False, "Дебил..."
        return total  # возвращаем массив типа [[baseid, friendid],...]


if __name__ == '__main__':
    pass
