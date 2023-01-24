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


def join_db_path(name: str):
    return os.path.join(base_db_path, name)


def create_data(qq: int, data: dict):
    dest = join_db_path('{}.json'.format(qq))
    if os.path.exists(dest):
        return
    with open(dest, 'w') as f:
        json.dump(data, f)


def load_data(qq: int):
    dest = join_db_path('{}.json'.format(qq))
    if not os.path.exists(dest):
        return None
    with open(dest, 'r') as f:
        return json.load(f)


def is_registered(qq: int):
    return load_data(qq) is not None


def write_data(qq: int, data: dict):
    dest = join_db_path('{}.json'.format(qq))
    with open(dest, 'w') as f:
        json.dump(data, f)


def length_increase(qq: int, length: float):
    user_data = load_data(qq)
    user_data['length'] += length
    # ensure fixed 2
    user_data['length'] = fixed_two_decimal_digits(
        user_data['length'], to_number=True)
    write_data(qq, user_data)


def length_decrease(qq: int, length: float):
    user_data = load_data(qq)
    user_data['length'] -= length
    # ensure fixed 2
    user_data['length'] = fixed_two_decimal_digits(
        user_data['length'], to_number=True)
    # TODO: 禁止负值，更好的提示
    if user_data['length'] < 0:
        user_data['length'] = 0
    write_data(qq, user_data)


def record_time(qq: int, key: str):
    user_data = load_data(qq)
    user_data[key] = get_now_time()
    write_data(qq, user_data)


def reset_daily_count(qq: int, key: str):
    user_data = load_data(qq)
    user_data[key] = 0
    write_data(qq, user_data)


def is_lock_daily_limited(qq: int):
    user_data = load_data(qq)
    current_count = user_data['daily_lock_count']
    is_outed = is_date_outed(user_data['latest_daily_lock'])
    if is_outed:
        reset_daily_count(qq, 'daily_lock_count')
        return False
    max = get_config('lock_daily_max')
    if current_count >= max:
        return True
    return False


def count_lock_daily(qq: int):
    user_data = load_data(qq)
    user_data['daily_lock_count'] += 1
    user_data['latest_daily_lock'] = get_now_time()
    write_data(qq, user_data)


def is_glue_daily_limited(qq: int):
    user_data = load_data(qq)
    current_count = user_data['daily_glue_count']
    is_outed = is_date_outed(user_data['latest_daily_glue'])
    if is_outed:
        reset_daily_count(qq, 'daily_glue_count')
        return False
    max = get_config('glue_daily_max')
    if current_count >= max:
        return True
    return False


def count_glue_daily(qq: int):
    user_data = load_data(qq)
    user_data['daily_glue_count'] += 1
    user_data['latest_daily_glue'] = get_now_time()
    write_data(qq, user_data)


def is_pk_daily_limited(qq: int):
    user_data = load_data(qq)
    current_count = user_data['daily_pk_count']
    is_outed = is_date_outed(user_data['latest_daily_pk'])
    if is_outed:
        reset_daily_count(qq, 'daily_pk_count')
        return False
    max = get_config('pk_daily_max')
    if current_count >= max:
        return True
    return False


def count_pk_daily(qq: int):
    user_data = load_data(qq)
    user_data['daily_pk_count'] += 1
    user_data['latest_daily_pk'] = get_now_time()
    write_data(qq, user_data)
