import sqlalchemy
import sqlite3
import os
#from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


class DB:

    class Rounds(sqlalchemy.orm.declarative_base()):
        __tablename__ = ''

        ID = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
        baseid = sqlalchemy.Column(sqlalchemy.Integer)
        friendid = sqlalchemy.Column(sqlalchemy.Integer)
        is_closed = sqlalchemy.Column(sqlalchemy.Integer)

    targetid = ''
    engine = None
    session = None
    metadata = None

    def __init__(self):
        self.engine = sqlalchemy.create_engine(f'sqlite:///db/{self.targetid}.db', echo=True)
        self.session = sessionmaker(autoflush=True, bind=self.engine)
        self.metadata = sqlalchemy.MetaData()

    def _sqlalchemy_create_db(self, targetid, roundy, typy='normal'):  # http://sparrigan.github.io/sql/sqla/2016/01/03/dynamic-tables.html
        # Если есть желание можно допилить, но в целом необходимости нет
        '''engine = sqlalchemy.create_engine(f'sqlite://db/{targetid}.db')
        conn = engine.connect()
        metadata = sqlalchemy.MetaData()

        make_session = sessionmaker(bind=engine)
        session = make_session()  # create a Session
        base = declarative_base()

        class MyTableClass(base):
            __tablename__ = 'myTableName'
            myFirstCol = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
            mySecondCol = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)

        base.metadata.create_table(engine)

        for i in range(roundy + 1):
            table_variable = sqlalchemy.Table(f'round{i}', metadata,
                                              sqlalchemy.Column('ID', sqlalchemy.Integer),
                                              sqlalchemy.Column('baseid', sqlalchemy.Integer),
                                              sqlalchemy.Column('friendid', sqlalchemy.Integer),
                                              sqlalchemy.Column('is_closed', sqlalchemy.Boolean)
                                              )
            metadata.create_all(engine)
            '''
        pass

    def create_db(self, roundy, typy='normal'):
        if not os.path.exists('db'):
            os.mkdir('db')

        conn = sqlite3.connect(f'db/{self.targetid}.db')  # или :memory: чтобы сохранить в RAM
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

    def sqlalchemy_insert_db(self, value, roundy, name='round'):
        user_table = f'{name}{roundy}'
        #self.Rounds.__tablename__ = user_table
        table = sqlalchemy.Table(user_table, self.metadata)
        #stmt = (sqlalchemy.insert(user_table).values(name='username', fullname='Full Username'))
        with self.engine.connect() as connection:
            query = table.insert(table).values(value)

if __name__ == '__main__':
    pass
