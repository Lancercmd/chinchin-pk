import os
from src.db import load_data, write_data
from src.main import message_processor

user_1 = 123456789
user_2 = 987654321
group = 123


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def wrap(user: int, message: str, at_qq: int = None, comment: str = None):
    if comment:
        print(bcolors.OKGREEN + "------" + comment + "------" + bcolors.ENDC)
    message_processor(
        message=message,
        qq=user,
        group=group,
        at_qq=at_qq
    )


base_db_path = os.path.join(os.path.dirname(__file__), 'src', 'data')
for file in os.listdir(base_db_path):
    os.remove(os.path.join(base_db_path, file))


def test2():
    wrap(user_1, '打胶', comment='没注册')
    wrap(user_1, '牛子', comment='注册')
    wrap(user_1, '打胶', user_2, comment='打胶别人失败')
    wrap(user_1, 'pk', user_2, comment='pk 别人失败')
    wrap(user_1, '🔒', user_2, comment='🔒别人失败')
    wrap(user_1, '牛子', comment='查牛子信息')

    wrap(user_2, '牛子', comment='对方注册')
    wrap(user_2, '牛子', comment='user 2 查牛子信息')
    wrap(user_2, '打胶', comment='user 2 自己打胶')
    wrap(user_2, '🔒我', comment='user 2 自己🔒自己')
    wrap(user_2, '牛子', user_1, comment='user 2 查牛子是否短了')
    wrap(user_2, 'pk', comment='None')
    wrap(user_2, '🔒', comment='None')
    wrap(user_2, '打胶', user_1, comment='user 2 打胶 user 1')
    wrap(user_2, '🔒', user_1, comment='user 2 🔒 user 1')
    wrap(user_2, 'pk', user_1, comment='user 2 pk user 1')
    wrap(user_1, '牛子', user_1, comment='user 1 查牛子是否变了')

    # max
    wrap(user_2, 'pk', user_1, comment='user 2 反复 pk +2')
    wrap(user_2, 'pk', user_1, comment='user 2 反复 pk +3')
    wrap(user_2, 'pk', user_1, comment='user 2 反复 pk +4')
    wrap(user_2, 'pk', user_1, comment='user 2 反复 pk +5')
    wrap(user_2, 'pk', user_1, comment='user 2 反复 pk +6')
    wrap(user_2, '🔒', user_1, comment='user 2 反复 🔒 +2')
    wrap(user_2, '🔒', user_1, comment='user 2 反复 🔒 +3')
    wrap(user_2, '🔒', user_1, comment='user 2 反复 🔒 +4')
    wrap(user_2, '🔒', user_1, comment='user 2 反复 🔒 +5')
    wrap(user_2, '🔒', user_1, comment='user 2 反复 🔒 +6')
    wrap(user_2, '打胶', user_1, comment='user 2 反复 打胶 +2')
    wrap(user_2, '打胶', user_1, comment='user 2 反复 打胶 +3')
    wrap(user_2, '打胶', user_1, comment='user 2 反复 打胶 +4')
    wrap(user_2, '打胶', user_1, comment='user 2 反复 打胶 +5')
    wrap(user_2, '打胶', user_1, comment='user 2 反复 打胶 +6')

    wrap(user_1, '牛子', comment='user 1 查牛子是否变了')
    wrap(user_1, '打胶', comment='user 1 反复自己打胶 +1')
    wrap(user_1, '打胶', comment='user 1 反复自己打胶 +2')
    wrap(user_1, '打胶', comment='user 1 反复自己打胶 +3')
    wrap(user_1, '打胶', comment='user 1 反复自己打胶 +4')
    wrap(user_1, '🔒我', comment='user 1 反复自己🔒自己 +1')
    wrap(user_1, '🔒我', comment='user 1 反复自己🔒自己 +2')
    wrap(user_1, '🔒我', comment='user 1 反复自己🔒自己 +3')
    wrap(user_1, '🔒我', comment='user 1 反复自己🔒自己 +4')

    # self
    wrap(user_1, 'pk', user_1, 'user 1 pk 自己')
    wrap(user_1, '🔒', user_1, 'user 1 🔒 自己')
    wrap(user_1, '打胶', user_1, 'user 1 打胶 自己')

    # 查信息
    wrap(user_1, '牛子', comment='user 1 查牛子信息')
    wrap(user_2, '牛子', comment='user 2 查牛子信息')

    # 隔日
    data = load_data(user_1)
    data['latest_daily_lock'] = '2020-01-01 00:00:01'
    data['pked_time'] = '2020-01-01 00:00:01'
    write_data(user_1, data)
    wrap(user_1, '牛子', comment='user 1 隔日查牛子信息')
    wrap(user_1, '🔒我', comment='user 1 🔒自己')

    # 大额惩罚机制
    data = load_data(user_1)
    data['length'] = 25
    data['latest_daily_lock'] = '2020-01-01 00:00:01'
    write_data(user_1, data)
    wrap(user_1, '牛子', comment='user 1 查牛子信息')
    wrap(user_1, '🔒我', comment='user 1 🔒自己 +1')
    wrap(user_1, '🔒我', comment='user 1 🔒自己 +2')
    wrap(user_1, '🔒我', comment='user 1 🔒自己 +3')
    wrap(user_1, '🔒我', comment='user 1 🔒自己 +4 max')
    wrap(user_1, '🔒', user_2, comment='user 1 🔒别人 max')
    wrap(user_1, '打胶', user_2, comment='user 1 打胶 user 2 max')
    wrap(user_1, '牛子', comment='user 1 查牛子信息')

    # 看别人牛子
    wrap(user_1, '看他牛子', user_2, comment='user 1 查 user 2 牛子信息')
    wrap(user_1, '看他牛子', comment='None')

test2()
