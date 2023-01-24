import os
from .utils import get_now_time, is_date_outed, fixed_two_decimal_digits
from .config import get_config

try:
    import ujson as json
except ImportError:
    import json

"""
TODO: use sqlite instead json
"""

base_db_path = os.path.join(os.path.dirname(__file__), 'data')

if not os.path.exists(base_db_path):
    os.mkdir(base_db_path)


class DB():

    @staticmethod
    def join_db_path(name: str):
        return os.path.join(base_db_path, name)

    @classmethod
    def create_data(cls, qq: int, data: dict):
        dest = cls.join_db_path('{}.json'.format(qq))
        if os.path.exists(dest):
            return
        with open(dest, 'w') as f:
            json.dump(data, f)

    @classmethod
    def load_data(cls, qq: int):
        dest = cls.join_db_path('{}.json'.format(qq))
        if not os.path.exists(dest):
            return None
        with open(dest, 'r') as f:
            return json.load(f)

    @classmethod
    def is_registered(cls, qq: int):
        return cls.load_data(qq) is not None

    @classmethod
    def write_data(cls, qq: int, data: dict):
        dest = cls.join_db_path('{}.json'.format(qq))
        with open(dest, 'w') as f:
            json.dump(data, f)

    @classmethod
    def length_increase(cls, qq: int, length: float):
        user_data = cls.load_data(qq)
        user_data['length'] += length
        # ensure fixed 2
        user_data['length'] = fixed_two_decimal_digits(
            user_data['length'], to_number=True)
        cls.write_data(qq, user_data)

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
        cls.write_data(qq, user_data)

    @classmethod
    def record_time(cls, qq: int, key: str):
        user_data = cls.load_data(qq)
        user_data[key] = get_now_time()
        cls.write_data(qq, user_data)

    @classmethod
    def reset_daily_count(cls, qq: int, key: str):
        user_data = cls.load_data(qq)
        user_data[key] = 0
        cls.write_data(qq, user_data)

    @classmethod
    def is_lock_daily_limited(cls, qq: int):
        user_data = cls.load_data(qq)
        current_count = user_data['daily_lock_count']
        is_outed = is_date_outed(user_data['latest_daily_lock'])
        if is_outed:
            cls.reset_daily_count(qq, 'daily_lock_count')
            return False
        max = get_config('lock_daily_max')
        if current_count >= max:
            return True
        return False

    @classmethod
    def count_lock_daily(cls, qq: int):
        user_data = cls.load_data(qq)
        user_data['daily_lock_count'] += 1
        user_data['latest_daily_lock'] = get_now_time()
        cls.write_data(qq, user_data)

    @classmethod
    def is_glue_daily_limited(cls, qq: int):
        user_data = cls.load_data(qq)
        current_count = user_data['daily_glue_count']
        is_outed = is_date_outed(user_data['latest_daily_glue'])
        if is_outed:
            cls.reset_daily_count(qq, 'daily_glue_count')
            return False
        max = get_config('glue_daily_max')
        if current_count >= max:
            return True
        return False

    @classmethod
    def count_glue_daily(cls, qq: int):
        user_data = cls.load_data(qq)
        user_data['daily_glue_count'] += 1
        user_data['latest_daily_glue'] = get_now_time()
        cls.write_data(qq, user_data)

    @classmethod
    def is_pk_daily_limited(cls, qq: int):
        user_data = cls.load_data(qq)
        current_count = user_data['daily_pk_count']
        is_outed = is_date_outed(user_data['latest_daily_pk'])
        if is_outed:
            cls.reset_daily_count(qq, 'daily_pk_count')
            return False
        max = get_config('pk_daily_max')
        if current_count >= max:
            return True
        return False

    @classmethod
    def count_pk_daily(cls, qq: int):
        user_data = cls.load_data(qq)
        user_data['daily_pk_count'] += 1
        user_data['latest_daily_pk'] = get_now_time()
        cls.write_data(qq, user_data)
