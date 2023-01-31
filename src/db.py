import os
from .utils import get_now_time, is_date_outed, fixed_two_decimal_digits
from .config import Config
import sqlite3

sql_ins = None


class Paths():
    @staticmethod
    def base_db_path_v1():
        return os.path.join(os.path.dirname(__file__), 'data')

    @staticmethod
    def base_db_dir():
        return os.path.join(os.path.dirname(__file__), 'data-v2')

    @classmethod
    def sqlite_path(cls):
        return os.path.join(cls.base_db_dir(), 'data.sqlite')


class MigrationHelper():
    @staticmethod
    def old_data_check():
        # check old v1 data exist and tip
        if os.path.exists(Paths.base_db_path_v1()):
            print(
                '[Chinchin::Deprecated]: 目录 src/data-v2 新数据已经初始化，旧 v1 版本数据 src/data 已经不再使用，可以备份后手动删除！')
            print(
                '[Chinchin::Deprecated]: 若使用了 scripts/database_migrate_python/migrate.py 备份脚本，默认会备份到 src/data-v1-backup 下面')


class Sql():
    def __init__(self):
        self.sqlite_path = Paths.sqlite_path()
        self.conn = sqlite3.connect(self.sqlite_path)
        self.cursor = self.conn.cursor()

    @staticmethod
    def __sql_create_table():
        return 'create table if not exists `users` (`qq` bigint, `length` float, `daily_lock_count` integer, `daily_pk_count` integer, `daily_glue_count` integer, `register_time` varchar(255), `latest_daily_lock` varchar(255), `latest_daily_pk` varchar(255), `latest_daily_glue` varchar(255), `pk_time` varchar(255), `pked_time` varchar(255), `glueing_time` varchar(255), `glued_time` varchar(255), `locked_time` varchar(255), primary key (`qq`));'

    @staticmethod
    def __sql_insert_single_data(data: dict):
        return f'insert into `users` (`daily_glue_count`, `daily_lock_count`, `daily_pk_count`, `glued_time`, `glueing_time`, `latest_daily_glue`, `latest_daily_lock`, `latest_daily_pk`, `length`, `locked_time`, `pk_time`, `pked_time`, `qq`, `register_time`) values ({data["daily_glue_count"]}, {data["daily_lock_count"]}, {data["daily_pk_count"]}, "{data["glued_time"]}", "{data["glueing_time"]}", "{data["latest_daily_glue"]}", "{data["latest_daily_lock"]}", "{data["latest_daily_pk"]}", {data["length"]}, "{data["locked_time"]}", "{data["pk_time"]}", "{data["pked_time"]}", {data["qq"]}, "{data["register_time"]}");'

    @staticmethod
    def __sql_select_single_data(qq: int):
        return f'select * from `users` where `qq` = {qq};'

    @staticmethod
    def __sql_check_table_exists():
        return 'select count(*) from sqlite_master where type = "table" and name = "users";'

    @staticmethod
    def __sql_update_single_data(data: dict):
        return f'update `users` set `length` = {data["length"]}, `register_time` = "{data["register_time"]}", `daily_lock_count` = {data["daily_lock_count"]}, `daily_pk_count` = {data["daily_pk_count"]}, `daily_glue_count` = {data["daily_glue_count"]}, `latest_daily_lock` = "{data["latest_daily_lock"]}", `latest_daily_pk` = "{data["latest_daily_pk"]}", `latest_daily_glue` = "{data["latest_daily_glue"]}", `pk_time` = "{data["pk_time"]}", `pked_time` = "{data["pked_time"]}", `glueing_time` = "{data["glueing_time"]}", `glued_time` = "{data["glued_time"]}", `locked_time` = "{data["locked_time"]}" where `qq` = {data["qq"]};'

    @staticmethod
    def __sql_get_data_counts():
        return 'select count(*) from `users`;'

    @classmethod
    def get_data_counts(cls) -> int:
        sql_ins.cursor.execute(cls.__sql_get_data_counts())
        one = sql_ins.cursor.fetchone()
        return one[0]

    @classmethod
    def insert_single_data(cls, data: dict):
        sql_ins.cursor.execute(cls.__sql_insert_single_data(data))
        sql_ins.conn.commit()

    @classmethod
    def select_data_by_qq(cls, qq: int):
        sql_ins.cursor.execute(cls.__sql_select_single_data(qq))
        one = sql_ins.cursor.fetchone()
        if one is None:
            return None
        return {
            'qq': one[0],
            'length': one[1],
            'daily_lock_count': one[2],
            'daily_pk_count': one[3],
            'daily_glue_count': one[4],
            'register_time': one[5],
            'latest_daily_lock': one[6],
            'latest_daily_pk': one[7],
            'latest_daily_glue': one[8],
            'pk_time': one[9],
            'pked_time': one[10],
            'glueing_time': one[11],
            'glued_time': one[12],
            'locked_time': one[13]
        }

    @classmethod
    def check_table_exists(cls):
        sql_ins.cursor.execute(cls.__sql_check_table_exists())
        one = sql_ins.cursor.fetchone()
        return one[0] == 1

    @classmethod
    def update_data_by_qq(cls, data: dict):
        sql_ins.cursor.execute(cls.__sql_update_single_data(data))
        sql_ins.conn.commit()

    @staticmethod
    def init_database():
        global sql_ins
        if sql_ins:
            return sql_ins
        if not os.path.exists(Paths.base_db_dir()):
            os.mkdir(Paths.base_db_dir())
        if not os.path.exists(Paths.sqlite_path()):
            open(Paths.sqlite_path(), 'w').close()
        sql_ins = Sql()
        # check `users` table exists
        if not sql_ins.check_table_exists():
            sql_ins.cursor.execute(sql_ins.__sql_create_table())
            sql_ins.conn.commit()
        MigrationHelper.old_data_check()
        return sql_ins

    def destroy(self):
        self.conn.close()


class DB():

    @staticmethod
    def create_data(data: dict):
        Sql.insert_single_data(data)

    @staticmethod
    def load_data(qq: int):
        return Sql.select_data_by_qq(qq)

    @classmethod
    def is_registered(cls, qq: int):
        return cls.load_data(qq) is not None

    @classmethod
    def write_data(cls, data: dict):
        Sql.update_data_by_qq(data)

    @staticmethod
    def get_data_counts():
        return Sql.get_data_counts()

    @classmethod
    def length_increase(cls, qq: int, length: float):
        user_data = cls.load_data(qq)
        user_data['length'] += length
        # ensure fixed 2
        user_data['length'] = fixed_two_decimal_digits(
            user_data['length'], to_number=True)
        cls.write_data(user_data)

    @classmethod
    def length_decrease(cls, qq: int, length: float):
        user_data = cls.load_data(qq)
        user_data['length'] -= length
        # ensure fixed 2
        user_data['length'] = fixed_two_decimal_digits(
            user_data['length'], to_number=True)
        # TODO: 禁止负值，更好的提示
        if user_data['length'] < 0:
            user_data['length'] = 0
        cls.write_data(user_data)

    @classmethod
    def record_time(cls, qq: int, key: str):
        user_data = cls.load_data(qq)
        user_data[key] = get_now_time()
        cls.write_data(user_data)

    @classmethod
    def reset_daily_count(cls, qq: int, key: str):
        user_data = cls.load_data(qq)
        user_data[key] = 0
        cls.write_data(user_data)

    @classmethod
    def is_lock_daily_limited(cls, qq: int):
        user_data = cls.load_data(qq)
        current_count = user_data['daily_lock_count']
        is_outed = is_date_outed(user_data['latest_daily_lock'])
        if is_outed:
            cls.reset_daily_count(qq, 'daily_lock_count')
            return False
        max = Config.get_config('lock_daily_max')
        if current_count >= max:
            return True
        return False

    @classmethod
    def count_lock_daily(cls, qq: int):
        user_data = cls.load_data(qq)
        user_data['daily_lock_count'] += 1
        user_data['latest_daily_lock'] = get_now_time()
        cls.write_data(user_data)

    @classmethod
    def is_glue_daily_limited(cls, qq: int):
        user_data = cls.load_data(qq)
        current_count = user_data['daily_glue_count']
        is_outed = is_date_outed(user_data['latest_daily_glue'])
        if is_outed:
            cls.reset_daily_count(qq, 'daily_glue_count')
            return False
        max = Config.get_config('glue_daily_max')
        if current_count >= max:
            return True
        return False

    @classmethod
    def count_glue_daily(cls, qq: int):
        user_data = cls.load_data(qq)
        user_data['daily_glue_count'] += 1
        user_data['latest_daily_glue'] = get_now_time()
        cls.write_data(user_data)

    @classmethod
    def is_pk_daily_limited(cls, qq: int):
        user_data = cls.load_data(qq)
        current_count = user_data['daily_pk_count']
        is_outed = is_date_outed(user_data['latest_daily_pk'])
        if is_outed:
            cls.reset_daily_count(qq, 'daily_pk_count')
            return False
        max = Config.get_config('pk_daily_max')
        if current_count >= max:
            return True
        return False

    @classmethod
    def count_pk_daily(cls, qq: int):
        user_data = cls.load_data(qq)
        user_data['daily_pk_count'] += 1
        user_data['latest_daily_pk'] = get_now_time()
        cls.write_data(user_data)

    @classmethod
    def is_pk_protected(cls, qq: int):
        user_data = cls.load_data(qq)
        min_length = Config.get_config('pk_guard_chinchin_length')
        if user_data['length'] <= min_length:
            return True
        return False

def lazy_init_database():
    Sql.init_database()
