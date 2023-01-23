import os
import ujson as json
import random
import utils

config_file_path = os.path.join(os.path.dirname(__file__), 'config.json')
cache = None


def read_config():
    # TODO: 检测 config.json 变化重新加载
    global cache
    if cache:
        return cache
    with open(config_file_path, 'r') as f:
        cache = json.load(f)
        return cache


def get_config(key: str):
    config = read_config()
    return config.get(key)


def new_chinchin_length():
    min = get_config('new_chinchin_length_random_min')
    max = get_config('new_chinchin_length_random_max')
    return utils.fixed_two_decimal_digits(
        min + (max - min) * random.random(),
        to_number=True
    )


def is_hit(key: str):
    rate = get_config(key)
    return random.random() < rate


def get_lock_me_punish_value():
    min = get_config('lock_me_negative_min')
    max = get_config('lock_me_negative_max')
    return utils.fixed_two_decimal_digits(
        min + (max - min) * random.random(),
        to_number=True
    )


def get_lock_plus_value():
    min = get_config('lock_plus_min')
    max = get_config('lock_plus_max')
    return utils.fixed_two_decimal_digits(
        min + (max - min) * random.random(),
        to_number=True
    )


def get_glue_plus_value():
    min = get_config('glue_plus_min')
    max = get_config('glue_plus_max')
    return utils.fixed_two_decimal_digits(
        min + (max - min) * random.random(),
        to_number=True
    )


def is_pk_win():
    return random.random() < 0.5


def get_pk_plus_value():
    min = get_config('pk_plus_min')
    max = get_config('pk_plus_max')
    return utils.fixed_two_decimal_digits(
        min + (max - min) * random.random(),
        to_number=True
    )


def get_pk_punish_value():
    min = get_config('pk_negative_min')
    max = get_config('pk_negative_max')
    return utils.fixed_two_decimal_digits(
        min + (max - min) * random.random(),
        to_number=True
    )


def get_glue_punish_value():
    min = get_config('glue_negative_min')
    max = get_config('glue_negative_max')
    return utils.fixed_two_decimal_digits(
        min + (max - min) * random.random(),
        to_number=True
    )


def get_lock_punish_with_strong_person_value():
    min = get_config('lock_me_negative_with_strong_person_min')
    max = get_config('lock_me_negative_with_strong_person_max')
    return utils.fixed_two_decimal_digits(
        min + (max - min) * random.random(),
        to_number=True
    )
