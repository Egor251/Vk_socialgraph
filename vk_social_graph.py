# -*- coding: utf-8 -*-
import os
import time
import sqlite3
from sqlalchemy import create_engine

from db import DB
from graph_tools import GraphTools
from utils import Utils

try:  # для решения Сашкиной проблемы
    # Python <= 3.9
    from collections import Iterable
except ImportError:
    # Python > 3.9
    from collections.abc import Iterable

try:
    import vk
except ImportError:
    try:
        os.system('pip install vk')
        import vk
    except ImportError:
        os.system('pip3 install vk')
        import vk

try:
    import networkx as nx
except ImportError:
    try:
        os.system('pip install networkx')
        import networkx as nx
    except ImportError:
        os.system('pip3 install networkx')
        import networkx as nx

try:
    import matplotlib.pyplot as plt
except ImportError:
    try:
        os.system('pip install matplotlib')
        import matplotlib.pyplot as plt
    except ImportError:
        os.system('pip3 install matplotlib')
        import matplotlib.pyplot as plt

try:
    from tqdm import tqdm
except ImportError:
    try:
        os.system('pip install tqdm')
        from tqdm import tqdm
    except ImportError:
        os.system('pip3 install tqdm')
        from tqdm import tqdm

try:
    from numba import njit
except ImportError:
    try:
        os.system('pip install numpy==1.20')
        os.system('pip install numba')
        from numba import njit
    except ImportError:
        os.system('pip3 install numpy==1.20')
        os.system('pip3 install numba')
        from numba import njit

try:
    import configparser
except ImportError:
    import ConfigParser as configparser

from create_config import create_config

os.environ["NUMBA_DISABLE_PERFORMANCE_WARNINGST"] = '1'


'''# Уникализирует элементы массива. Ускорено numba
@njit
def unique(list1):
    unique = []
    for number in list1:
        if number not in unique:
            unique.append(number)
    return unique


# Уникализирует элементы массива. Не ускорено numba)
def usual_unique(list1):
    unique = []
    for number in tqdm(list1):
        if number not in unique:
            unique.append(number)
    return unique
'''
#unique = Utils().unique()
#usual_unique = Utils.usual_unique()


class VK:

    config_path = "config.ini"
    #token = 'dc0fb051dc0fb051dc0fb051b8dc575004ddc0fdc0fb05183aa6f4261752c87f7a3fa69'
    config = configparser.ConfigParser()
    config.read(config_path)
    token = config.get("API", "VK_api")
    vk_api = vk.API(access_token=token)
    targetid = ''

    def __init__(self):
        if not os.path.exists(self.config_path):
            create_config(self.config_path)
        config = configparser.ConfigParser()
        config.read(self.config_path)

    # Из готовой базы ищет пересечения
    def get_connections_from_db(self, roundy, type='normal'):
        conn = sqlite3.connect(f'db/{self.targetid}.db')
        cursor = conn.cursor()
        total = []
        if type == 'normal':
            total += cursor.execute(f'select baseid, friendid from round0')
            for i in tqdm(range(1, roundy + 1)):
                cursor.execute(f'select baseid, friendid from round{i - 1}')
                a = Utils().graph_data_preparation(cursor.fetchall())
                b = []
                for j in tqdm(a):
                    sql = f'select baseid, friendid from round{i} where friendid = {j[1]}'
                    cursor.execute(sql)
                    b += Utils().graph_data_preparation(cursor.fetchall())
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
                    b += Utils().graph_data_preparation(cursor.fetchall())
            total += Utils().graph_data_preparation(tmp)
            total += b
        else:
            assert False, "Дебил..."
        return total  # возвращаем массив типа [[baseid, friendid],...]

    # Восстанавливает прогресс в случае досрочной остановки поиска и перезапуска
    def repair_process(self, roundy):
        conn = sqlite3.connect(f'db/{self.targetid}.db')
        cursor = conn.cursor()
        current_round = 0
        sql = f"Select * FROM round{roundy} WHERE baseid = {0};"
        cursor.execute(sql)
        full = cursor.fetchall()
        current_friend = ''
        if len(full) != 0:
            current_round = -1
        else:
            for i in range(roundy + 2):
                cursor.execute(f"Select name FROM sqlite_master WHERE type='table' AND name='round{i}';")
                if cursor.fetchone() is None:
                    current_round = i - 1
                    for j in range(current_round, -1, -1):
                        cursor.execute(f"Select * FROM round{roundy};")
                        if cursor.fetchone() is not None:
                            current_round = j
                            break
                        if j == 0:
                            current_round = 0
                    break
            if current_round > 0:
                sql = f"SELECT * FROM round{current_round} WHERE ID = (SELECT MAX(ID) FROM round{current_round});"
                cursor.execute(sql)
                current_friend = cursor.fetchall()[0][1]
        return current_round, current_friend  # Возвращает массив типа [roundy, friendid]

    # Функция сохранения базы в gexf файле
    def save_data(self, G, filename="graph.gexf"):
        nx.write_gexf(G, filename, encoding='utf-8', prettyprint=True, version='1.2draft')

    # Предельно тупой поиск друзей
    def friends_search(self, targetid, roundy, rep=0):

        if not os.path.exists('db'):
            os.mkdir('db')
        if os.listdir('db').count(f'{targetid}.db') != 0:
            rep = 1
        else:
            DB().create_db(roundy, 'normal')

        conn = sqlite3.connect(f'db/{targetid}.db')
        cursor = conn.cursor()
        start_round = 1
        start_friend = None
        if rep == 1:
            tmp_tupple = self.repair_process(roundy)
            start_round = tmp_tupple[0]
            start_friend = tmp_tupple[1]
        else:
            self.insert_db(self.get_members(self.targetid, 0), 0)
        start = 0
        if start_round != -1:
            for i in range(int(start_round), roundy + 1):
                #TODO: friends search: при остановке на первом же круге выбрасывает ошибку sql в round-1
                sql = f'SELECT friendid from round{i - 1} WHERE is_closed = 0'
                cursor.execute(sql)
                friends = cursor.fetchall()
                friends = Utils().unique(friends)
                try:
                    start = friends.index((start_friend,))
                except Exception:
                    pass
                for fr in tqdm(range(start, len(friends))):
                    self.insert_db(self.get_members(friends[fr][0], fr), i)
                self.insert_db([[0, 0, 0, 1]], i)

    # получаем массив уникальных id
    def all_users_list(self, a):
        all_users = []
        for b in a:
            #TODO: all_users_list: проверить, оптимизировать
            all_users.append(b[0])
            all_users.append(b[1])
        try:
            all_users = Utils().unique(all_users)
        except Exception:
            all_users = Utils().usual_unique(all_users)
        return all_users  # возращает массив типа [id, ..]

    def node_attr_preparation(self, lis):
        all_users = self.all_users_list(lis)
        node_attrs = {}
        for item in tqdm(all_users):
            node_attrs[item] = self.get_full_member_data(item)
        return all_users, node_attrs

    '''# Формирует итоговый граф
    def get_graph(self, lis, all_users, node_attrs):
        print('формируем граф')

        G = nx.Graph()
        G.add_weighted_edges_from(lis)
        #all_users = self.all_users_list(lis)
        print(f'Всего узлов графа: {len(all_users)}')
        #for item in tqdm(all_users):
            #node_attrs = {item: self.get_full_member_data(item)}
        nx.set_node_attributes(G, node_attrs)

        color_map = []
        labels = {}
        for node in G:  # формируем карту цветов из атрибутов нод
            labels[node] = G.nodes[node]['name']
            try:
                if G.nodes[node]['sex'] == 1:
                    color_map.append('red')
                elif G.nodes[node]['sex'] == 2:
                    color_map.append('blue')
                else:
                    color_map.append('blue')
            except Exception:
                color_map.append('gold')

        options = {
            'node_color': color_map,
            'node_size': 15,
            'width': 0.1,
            'labels': labels
        }
        try:  # Вообще хз, но только так работает!
            nx.draw(G, **options)
        except Exception:
            pass
        plt.show()
        return G  # Возвращает граф с которым дальше может работать networkx'''

    # Получаем id если введён ник
    def checker(self, id):
        if type(id) is str:
            first = self.vk_api.users.get(user_ids=id, fields='name', v=5.92)
            return int(first[0]['id'])
        elif type(id) is int:
            return id
        else:
            print('хрень')

    # Делаем запросы к вк по каждому пользователю, берём все интересующие данные и мучительно парсим
    def get_full_member_data(self, userid):
        first = self.vk_api.users.get(user_id=userid,
                                 fields=' sex, bdate, city, country, home_town, photo_50, contacts, '
                                        'site, education, universities, schools, status, followers_count, occupation, '
                                        'nickname, relation, connections, exports, activities, '
                                        'interests, music, movies, tv, books, games, about, quotes, timezone, screen_name, '
                                        'maiden_name, career', v=5.92)
        tmp_dict = {}
        if first != []:
            for i in first[0]:
                if first[0][i] != '' and first[0][i] != []:
                    if isinstance(first[0][i], list):
                        first[0][i] = first[0][i][0]
                        if first[0][i] == '' or first[0][i] == []:
                            pass
                    if i == 'city' or i == 'country':
                        first[0][i] = first[0][i]['title']
                    elif i == 'first_name':
                        tmp_dict['name'] = f"{first[0]['last_name']} {first[0]['first_name']}"
                    elif i == 'last_name':
                        pass
                    elif i == 'occupation':
                        tmp_dict[first[0][i]['type']] = first[0][i]['name']
                    elif i == 'status_audio':
                        pass
                    elif i == 'personal':
                        pass
                    elif i == 'relation_partner':
                        tmp_dict['relation_partners_name'] = first[0][i]['last_name'] + first[0][i]['first_name']
                        tmp_dict['relation_partners_id'] = first[0][i]['id']
                    elif i == 'career':
                        try:
                            tmp_dict['career_company'] = first[0][i]['company']
                            tmp_dict['career_position'] = first[0][i]['position']
                        except KeyError:
                            pass
                    elif i == 'universities':
                        tmp_dict['university_name'] = first[0][i]['name']
                        try:
                            str_tmp = first[0][i]['faculty_name'].replace('\r', '')
                            str_tmp = str_tmp.replace('\n', '')
                            tmp_dict['university_faculty'] = str_tmp
                        except KeyError:
                            pass
                    elif i == 'schools':
                        tmp_dict['school'] = first[0][i]['name']
                        try:
                            tmp_dict['school_dates'] = f"{first[0][i]['year_from']} : + {first[0][i]['year_to']}"
                        except KeyError:
                            try:
                                tmp_dict['school_to'] = first[0][i]['year_to']
                            except KeyError:
                                pass
                    else:
                        if isinstance(first[0][i], dict):
                            print(f'{i} : {first[0][i]}')
                            raise ValueError
                        tmp_dict[i] = first[0][i]
        else:
            tmp_dict['name'] = 'unknown'
        return tmp_dict  # возвращаем словарь со всей полезной информацией с аккаунта

    # Совершает запросы к vk выводит друзей в виде списка
    def get_members(self, userid, id):  # Функция формирования друзей в виде списка
        first = self.vk_api.friends.get(user_id=userid, fields='id', v=5.92)
        members = []
        for i in range(first['count']):
            try:
                members.append([int(str(id) + str(i)), str(userid), str(first['items'][i]['id']),
                                int(first['items'][i]['is_closed'])])
            # members_base[str(first['items'][i]['id'])] = first['items'][i]['first_name'] + ' ' + first['items'][i]['last_name']
            except KeyError:
                pass
        return members  # возвращаем массив типа [[уникальный (наверное) id запроса, baseid,
        # friendid, закрыт профиль или нет],...]

    '''# Создаёт базу (очевидно же..)
    def create_db(self, targetid, roundy, typy='normal'):
        if not os.path.exists('db'):
            os.mkdir('db')

        conn = sqlite3.connect(f'db/{targetid}.db')  # или :memory: чтобы сохранить в RAM
        cursor = conn.cursor()
        if typy == 'normal':
            # cursor.execute("""CREATE TABLE IF NOT EXISTS target(userid INT PRIMARY KEY, first_name TEXT, last_name TEXT, sex INT, city TEXT, country TEXT, birth_date TEXT, company TEXT, position TEXT, university TEXT, faculty TEXT, graduation INT, education_status TEXT, home_town TEXT, is_closed INT); """)
            for i in range(roundy + 1):
                cursor.execute(f"""CREATE TABLE IF NOT EXISTS round{i} (
                   ID INT, baseid INT, friendid INT, is_closed INT);
                """)
            conn.commit()
        elif typy == 'hidden':
            for i in range(5):
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
            assert False, "Дебил..."
'''
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

    # Поиск друзей скрытого пользователя

    def get_hidden(self, start, target, deep):  # принимает начальную точку поиска (можно несколько массивом),

        # цель и глубину поиска
        rep = 0
        if not os.path.exists('db'):  # проверка на существование папки и бд
            os.mkdir('db')
        if os.listdir('db').count(f'{targetid}.db') != 0:
            rep = 1
        else:
            DB().create_db(roundy, 'hidden')

        conn = sqlite3.connect(f'db/{targetid}.db')
        cursor = conn.cursor()
        start_round = 1
        start_friend = None
        if rep == 1:
            tmp_tupple = self.repair_process(deep)
            start_round = tmp_tupple[0]
            start_friend = tmp_tupple[1]
        else:
            self.insert_db(self.get_members(start, 0), 0)
        if start_round != -1:
            DB().create_db(deep, 'hidden')
            if isinstance(start, int):
                start = [start]
            for start_point in start:
                self.insert_db(self.get_members(start_point, 0), 0, 'attempt')
            i = 0
            zbs = None
            while zbs is None:  # ищем до тех пор, пока не найдём хоть одного друга
                i += 1
                sql = f'SELECT friendid from attempt{i - 1} WHERE is_closed = 1'
                cursor.execute(sql)
                friends = cursor.fetchall()
                friends = Utils().unique(friends)
                if friends.count((target,)) != 0:
                    zbs = 1
                else:
                    sql = f'SELECT friendid from attempt{i - 1} WHERE is_closed = 0'
                    cursor.execute(sql)
                    friends = cursor.fetchall()
                    friends = Utils().unique(friends)
                    for fr in tqdm(range(len(friends))):
                        self.insert_db(self.get_members(friends[fr][0], fr), i, 'attempt')
                    self.insert_db([0, 'FULL', 'FULL', 2], i, 'attempt')

            sql = f'SELECT baseid from attempt{i - 1} WHERE friendid = {target}'  # Начинаем основной цикл
            cursor.execute(sql)
            entrypoint = cursor.fetchall()
            entrypoint = Utils().unique(entrypoint)
            print(f'Найдено точек входа: {len(entrypoint)}')
            for ent in entrypoint:
                self.insert_db(self.get_members(ent, 0), 0, 'round')
            if start_round == 0:
                start_round += 1
            for i in range(start_round, deep + 1):
                sql = f'SELECT friendid from round{i - 1} WHERE is_closed = 0;'
                cursor.execute(sql)
                friends = cursor.fetchall()
                friends = Utils().usual_unique(friends)
                try:
                    start_friend = friends.index((start_friend,))
                except ValueError:
                    start_friend = 0
                check = 0
                for fr in tqdm(range(start_friend, len(friends))):
                    self.insert_db(self.get_members(friends[fr][0], fr), i)

                    sql = f'SELECT baseid, is_closed from round{i - 1} WHERE friendid = {target}'
                    cursor.execute(sql)
                    check = cursor.fetchall()
                    try:
                        check = Utils().unique(check)
                        value = []
                        for item in check:
                            value.append([target, item[0], item[1]])
                        for val in value:
                            cursor.executemany(f"INSERT INTO result VALUES (?,?,?)", (val,))
                            conn.commit()
                    except ValueError:
                        check = 0
                print(f'Раунд: {i}')
                print(f'Найдено друзей: {len(check)}')
                self.insert_db([[-1, 0, 0, 1]], i)  # отметка о полном заполнении таблицы

    def open_account_start(self, targetid, roundy):
        self.targetid = self.checker(targetid)
        self.friends_search(self.targetid, roundy)

        lis = Utils().graph_data_preparation(self.get_connections_from_db(roundy))
        all_users, node_attrs = self.node_attr_preparation(lis)

        self.save_data(GraphTools().get_graph(lis, all_users, node_attrs), f'{targetid}.gexf')

    def hidden_account_start(self, start, targetid, roundy):
        self.get_hidden(self.checker(start), self.checker(targetid), 2)

        lis = Utils().graph_data_preparation(self.get_connections_from_db(roundy, 'hidden'))
        all_users, node_attrs = self.node_attr_preparation(lis)

        self.save_data(GraphTools().get_graph(lis, all_users, node_attrs), f'{targetid}.gexf')

if __name__ == "__main__":
    os.environ["NUMBA_DISABLE_PERFORMANCE_WARNINGST"] = '1'
    token = ""
    #session = vk.Session(access_token=token)  # Авторизация
    #vk_api = vk.API(session)
    vk_api = vk.API(access_token=token)
    #############

    # startid = ''   # С кого начинаем поиск (для скрытого профиля)
    targetid = 'sanyafinik'  # Кого пробиваем (id или ник)
    roundy = 2  # число раундов. 0 - бесполезно, 1 - пару минут, 2 - час или больше, 3 - 1 или 2 дня, 4 - дурак, чтоль?

    #############

    # start = checker(startid)  # Раскоментить для скрытого профиля
    #targetid = VK().checker(targetid)

    # для удобства тестирования, при использовании по назначению удалить или закоментировать
    '''if not os.path.exists('db'):
        os.mkdir('db')
    try:
        os.remove(f'db/{targetid}.db')
    except Exception:
        pass'''

    VK().open_account_start(targetid, roundy)

    # поиск скрытого пользователя
    # VK().get_hidden(start, targetid, 2)
    # VK().save_data(VK().get_graph(VK().data_preparation(VK().get_connections_from_db(roundy, 'hidden'))), f'{targetid}.gexf')

    # Поиск обычного пользователя
    #VK().friends_search(targetid, roundy)
    #VK().save_data(VK().get_graph(VK().data_preparation(VK().get_connections_from_db(roundy))), f'{targetid}.gexf')

    # time_test(first)

# Ограничение vk: 20 запросов в секунду, остальное - потери
# Можно использовать Asynco на get_members и insert_db. Строго говоря, они могут действовать независимо

# import scipy, pyyaml   не забыть узнать почему я год назад это написал!

# скачать https://gephi.org/
