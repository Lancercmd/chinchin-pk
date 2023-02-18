import os
import time
from src.db import DB, Sql
from src.main import message_processor, KEYWORDS
from src.utils import get_object_values, ArrowUtil, fixed_two_decimal_digits
from src.config import Config
from src.farm import FarmSystem
from src.friends import FriendsSystem
import sys

user_1 = 123456789
user_2 = 987654321
user_3 = 1233
user_1_nickname = '用户1'
user_2_nickname = "'; select true; --"
group = 123

get_now_time = ArrowUtil.get_now_time

k = get_object_values(KEYWORDS)
print(k)

def clear_logger():
    snapshot_dir = os.path.join(os.path.dirname(__file__), '__snapshot__')
    logger_dirs = [os.path.join(snapshot_dir, d) for d in os.listdir(snapshot_dir) if os.path.isdir(os.path.join(snapshot_dir, d))]
    max_file_count = 10
    for logger_dir in logger_dirs:
        files = os.listdir(logger_dir)
        if len(files) > max_file_count:
            files.sort(key=lambda x: os.path.getmtime(os.path.join(logger_dir, x)))
            for file in files[:len(files) - max_file_count]:
                print(f'remove {os.path.join(logger_dir, file)}')
                os.remove(os.path.join(logger_dir, file))

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


snapshot = []

def wrap_print_only(title: str, comment):
    print(bcolors.OKGREEN + "------" + title + "------" + bcolors.ENDC)
    is_string = isinstance(comment, str)
    if is_string:
        print(comment)
        snapshot.append(comment)
    else:
        # dict to string
        dictToString = '\n'.join([f'{key}: {value}' for (key, value) in comment.items()])
        print(dictToString)
        snapshot.append(dictToString)
        

def wrap(user: int, message: str, at_qq: int = None, comment: str = None):
    if comment:
        print(bcolors.OKGREEN + "------" + comment + "------" + bcolors.ENDC)
        snapshot.append(comment)

    def impl_send_message(qq: int, group: int, message: str):
        print(message)
        snapshot.append(message)
    nickname = None
    if user == user_1:
        nickname = user_1_nickname
    elif user == user_2:
        nickname = user_2_nickname
    message_processor(
        message=message,
        qq=user,
        group=group,
        at_qq=at_qq,
        nickname=nickname,
        impl_send_message=impl_send_message
    )


log_arg = ''


def write_snapshot():
    global snapshot, log_arg
    timestamp = int(time.time())
    dir = f'./__snapshot__/{log_arg}'
    if not os.path.exists(dir):
        os.makedirs(dir)
    with open(f'{dir}/snapshot-{timestamp}.txt', 'w') as f:
        f.write('\n'.join(snapshot))


def clear_database():
    base_db_path = os.path.join(os.path.dirname(__file__), 'src', 'data-v2')
    if os.path.exists(base_db_path):
        print('remove old data')
        os.system(f'rm -rf {base_db_path}')


def arg(str: str):
    match = len(sys.argv) > 1 and sys.argv[1] == str
    if match:
        print(f'arg: {str}')
        global log_arg
        log_arg = f'{str}'
    return match


def test_legacy():

    wrap(user_1, '打胶', comment='没注册')
    wrap(user_1, '牛子', comment='没注册')
    wrap(user_1, '注册牛子', comment='注册')
    wrap(user_1, '打胶', user_2, comment='打胶别人失败')
    wrap(user_1, 'pk', user_2, comment='pk 别人失败')
    wrap(user_1, '🔒', user_2, comment='🔒别人失败')
    wrap(user_1, '牛子', comment='查牛子信息')

    wrap(user_2, '牛子', comment='没注册')
    wrap(user_2, '注册牛子', comment='对方注册')
    wrap(user_2, '牛子', comment='user 2 查牛子信息')
    wrap(user_2, '打胶', comment='user 2 自己打胶 l+1')
    wrap(user_2, '🔒我', comment='user 2 自己🔒自己 s+1')
    wrap(user_2, '牛子', user_1, comment='user 2 查牛子是否短了')
    wrap(user_2, 'pk', comment='None')
    wrap(user_2, '🔒', comment='None')
    wrap(user_2, '打胶', user_1, comment='user 2 打胶 user 1 l+2')
    wrap(user_2, '🔒', user_1, comment='user 2 🔒 user 1 s+2')
    wrap(user_2, 'pk', user_1, comment='user 2 pk user p+1')
    wrap(user_1, '牛子', user_1, comment='user 1 查牛子是否变了')

    # cd
    wrap(user_2, 'pk', user_1, comment='user 2 反复 pk p+2')
    wrap(user_2, 'pk', user_1, comment='user 2 反复 pk p+3')
    wrap(user_2, 'pk', user_1, comment='user 2 反复 pk p+4')
    wrap(user_2, 'pk', user_1, comment='user 2 反复 pk p+5 cd')
    wrap(user_2, 'pk', user_1, comment='user 2 反复 pk p+6 cd')
    wrap(user_2, '🔒', user_1, comment='user 2 反复 🔒 s+3')
    wrap(user_2, '🔒', user_1, comment='user 2 反复 🔒 s+4')
    wrap(user_2, '🔒', user_1, comment='user 2 反复 🔒 s+5 cd')
    wrap(user_2, '🔒', user_1, comment='user 2 反复 🔒 s+6 cd')
    wrap(user_2, '打胶', user_1, comment='user 2 反复 打胶 l+3')
    wrap(user_2, '打胶', user_1, comment='user 2 反复 打胶 l+4')
    wrap(user_2, '打胶', user_1, comment='user 2 反复 打胶 l+5 cd')
    wrap(user_2, '打胶', user_1, comment='user 2 反复 打胶 l+6 cd')

    wrap(user_1, '牛子', comment='user 1 查牛子是否变了')
    wrap(user_1, '打胶', comment='user 1 反复自己打胶 l+1')
    wrap(user_1, '打胶', comment='user 1 反复自己打胶 l+2')
    wrap(user_1, '打胶', comment='user 1 反复自己打胶 l+3')
    wrap(user_1, '打胶', comment='user 1 反复自己打胶 l+4')
    wrap(user_1, '打胶', comment='user 1 反复自己打胶 l+5 cd')
    wrap(user_1, '🔒我', comment='user 1 反复自己🔒自己 s+1')
    wrap(user_1, '🔒我', comment='user 1 反复自己🔒自己 s+2')
    wrap(user_1, '🔒我', comment='user 1 反复自己🔒自己 s+3')
    wrap(user_1, '🔒我', comment='user 1 反复自己🔒自己 s+4')
    wrap(user_1, '🔒我', comment='user 1 反复自己🔒自己 s+5 cd')

    # self
    wrap(user_1, 'pk', user_1, 'user 1 pk 自己 p+1')
    wrap(user_1, '🔒', user_1, 'user 1 🔒 自己 s+6 cd')
    wrap(user_1, '打胶', user_1, 'user 1 打胶 自己 l+6 cd')

    # 查信息
    wrap(user_1, '牛子', comment='user 1 查牛子信息')
    wrap(user_2, '牛子', comment='user 2 查牛子信息')

    # 隔日
    data = DB.load_data(user_1)
    data['latest_daily_lock'] = '2020-01-01 00:00:01'
    data['pked_time'] = '2020-01-01 00:00:01'
    DB.write_data(data)
    wrap(user_1, '牛子', comment='user 1 隔日查牛子信息')
    wrap(user_1, '🔒我', comment='user 1 🔒自己 l+1')
    wrap(user_1, '🔒我', comment='user 1 🔒自己 l+2')
    wrap(user_1, '🔒我', comment='user 1 🔒自己 l+3')
    wrap(user_1, '🔒我', comment='user 1 🔒自己 l+4')
    wrap(user_1, '🔒我', comment='user 1 🔒自己 l+5 cd')

    # 大额惩罚机制
    data = DB.load_data(user_1)
    data['length'] = 25
    data['latest_daily_lock'] = '2020-01-01 00:00:01'
    DB.write_data(data)
    wrap(user_1, '牛子', comment='大额惩罚机制 user 1 查牛子信息')
    wrap(user_1, '🔒我', comment='user 1 🔒自己 l+1')
    wrap(user_1, '🔒我', comment='user 1 🔒自己 l+2')
    wrap(user_1, '🔒我', comment='user 1 🔒自己 l+3')
    wrap(user_1, '🔒我', comment='user 1 🔒自己 l+4')
    wrap(user_1, '🔒我', comment='user 1 🔒自己 l+5 cd')
    wrap(user_1, '🔒', user_2, comment='user 1 🔒别人 l+6 cd')

    # max
    data = DB.load_data(user_1)
    data['daily_lock_count'] = 6
    data['daily_glue_count'] = 5
    data['latest_daily_glue'] = get_now_time()
    data['daily_pk_count'] = 6
    data['latest_daily_pk'] = get_now_time()
    DB.write_data(data)
    wrap(user_1, '🔒', user_2, comment='user 1 🔒 user 2 max')
    wrap(user_1, '打胶', user_2, comment='user 1 打胶 user 2')
    wrap(user_1, '打胶', user_2, comment='user 1 打胶 user 2 max')
    wrap(user_1, 'pk', user_2, comment='user 1 pk user 2 max')

    # 看别人牛子
    wrap(user_1, '看他牛子', user_2, comment='user 1 查 user 2 牛子信息')
    wrap(user_1, '看他牛子', comment='None')

    # pk保护
    data = DB.load_data(user_1)
    data['length'] = 5
    DB.write_data(data)
    data = DB.load_data(user_2)
    data['latest_daily_pk'] = '2020-01-01 00:00:01'
    DB.write_data(data)
    wrap(user_2, 'pk', user_1, comment='user 2 pk user 1 触发 pk 保护')
    wrap(user_2, 'pk', user_1, comment='user 2 pk user 1 触发 pk 保护 +2')

    # pk 超过 100% 不可能赢
    data = DB.load_data(user_1)
    data['length'] = 50
    data['latest_daily_pk'] = '2020-01-01 00:00:01'
    DB.write_data(data)
    data = DB.load_data(user_2)
    data['length'] = 101
    DB.write_data(data)
    wrap(user_1, 'pk', user_2, comment='user 1 pk user 2 超过 100% 不可能赢')
    wrap(user_1, 'pk', user_2, comment='user 1 pk user 2 超过 100% 不可能赢 + 1')
    wrap(user_1, 'pk', user_2, comment='user 1 pk user 2 超过 100% 不可能赢 + 2')
    wrap(user_1, 'pk', user_2, comment='user 1 pk user 2 超过 100% 不可能赢 + 3')
    wrap(user_1, 'pk', user_2, comment='user 1 pk user 2 超过 100% 不可能赢 + 4')

    # pk 在 100% 有可能赢
    data = DB.load_data(user_1)
    data['length'] = 60
    data['latest_daily_pk'] = '2020-01-01 00:00:01'
    DB.write_data(data)
    data = DB.load_data(user_2)
    data['length'] = 100
    DB.write_data(data)
    wrap(user_1, 'pk', user_2, comment='user 1 pk user 2 在 100% 有可能赢')
    wrap(user_1, 'pk', user_2, comment='user 1 pk user 2 在 100% 有可能赢 + 1')
    wrap(user_1, 'pk', user_2, comment='user 1 pk user 2 在 100% 有可能赢 + 2')
    wrap(user_1, 'pk', user_2, comment='user 1 pk user 2 在 100% 有可能赢 + 3')

def test_nickname():
    wrap(user_1, '注册牛子', comment='1 注册')
    wrap(user_2, '注册牛子', comment='2 注册')
    wrap(user_3, '注册牛子', comment='3 注册')

    # 查排名
    wrap(user_1, '牛子排名', comment='user 1 查排名')

    # 删掉 user_3 的 info 表记录，模拟增量场景
    Sql.sub_table_info.delete_single_data(user_3)

    # 改名字
    global user_1_nickname
    user_1_nickname = '用户1新名字'
    wrap(user_1, '牛子排名', comment='user 1 改名再查排名')


def test_rebirth():
    wrap(user_1, '注册牛子', comment='1 注册')
    wrap(user_2, '注册牛子', comment='2 注册')

    wrap(user_1, '牛子转生', comment='user 1 不能转生')

    data = DB.load_data(user_1)
    data['length'] = 199
    DB.write_data(data)
    wrap(user_1, '牛子转生', comment='user 1 不能转生 +1')

    data = DB.load_data(user_1)
    data['length'] = 200
    DB.write_data(data)
    wrap(user_1, '牛子转生', comment='user 1 一转')

    wrap(user_1, '牛子', comment='user 1 查个人信息')

    wrap(user_1, '牛子转生', comment='user 1 不能转生')

    data = DB.load_data(user_1)
    data['length'] = 1000
    DB.write_data(data)
    wrap(user_1, '牛子转生', comment='user 1 积攒太多再二转')
    wrap(user_1, '牛子', comment='user 1 查个人信息')
    wrap(user_1, '牛子转生', comment='user 1 三转')
    wrap(user_1, '牛子', comment='user 1 查个人信息')

    wrap(user_1, '牛子转生', comment='user 1 不能再转 +1')
    wrap(user_1, '牛子转生', comment='user 1 不能再转 +2')
    wrap(user_1, '牛子转生', comment='user 1 不能再转 +3')
    wrap(user_1, '牛子排行', comment='user 1 查排行')

    data = DB.load_data(user_2)
    data['length'] = 200
    DB.write_data(data)
    wrap(user_2, '牛子转生', comment='user 2 一转')
    wrap(user_2, '牛子', comment='user 2 查信息')
    wrap(user_1, 'pk', at_qq=user_2, comment='user 1 PK user 2，不能打掉转')
    Config.modify_config_in_runtime('pk_negative_min', 1)
    wrap(user_1, 'pk', at_qq=user_2, comment='user 1 PK user 2，预期 3 转加权伤害')
    wrap(user_2, '牛子', comment='user 2 查信息')
    wrap(user_2, '🔒我', comment='user 2 净长度 0 但可以🔒自己')

    Config.modify_config_in_runtime('glue_plus_min', 1.5)
    wrap(user_1, '打胶', comment='user 1 打胶，预期 3 转加权')

    wrap(user_3, '注册牛子', comment='3 注册')
    data = DB.load_data(user_3)
    data['length'] = 0
    DB.write_data(data)
    Config.modify_config_in_runtime('glue_self_negative_prob', 1)
    wrap(user_3, '打胶', comment='user 3 打胶')
    wrap(user_3, '牛子', comment='user 3 查信息')

def test_badge():
    wrap(user_1, '注册牛子', comment='1 注册')
    wrap(user_2, '注册牛子', comment='2 注册')

    # lock
    data = DB.load_data(user_1)
    data['length'] = 50
    DB.write_data(data)
    wrap(user_1, '🔒我', comment='1 锁自己 + 1')
    wrap(user_1, '🔒我', comment='1 锁自己 + 2')
    wrap(user_1, '🔒我', comment='1 锁自己 + 3')
    wrap(user_1, '锁', at_qq=user_2, comment='1 锁 2')

    # glue
    wrap(user_1, '打胶', comment='1 打胶自己')
    wrap(user_1, '打胶', at_qq=user_2, comment='1 打胶 2')

    # pk
    wrap(user_1, 'pk', at_qq=user_2, comment='1 pk 2 成功')
    data = DB.load_data(user_2)
    data['length'] = 1000
    DB.write_data(data)
    wrap(user_1, 'pk', at_qq=user_2, comment='1 pk 2 失败')

    # data check
    data = Sql.sub_table_badge.select_single_data(user_1)
    wrap_print_only('检查数据库', data)

    # 模拟 user 2 pk 获得一个成就
    wrap(user_1, '牛子成就', comment='1 查成就，没有东西')
    wrap(user_1, 'pk', at_qq=user_2, comment='1 pk 2 失败，没有任何反应')
    user_2_badge_data = Sql.sub_table_badge.select_single_data(user_2)
    user_2_badge_data['pk_win_count'] = 49
    user_2_badge_data['pk_plus_length_total'] = 50
    Sql.sub_table_badge.update_single_data(user_2_badge_data)

    wrap(user_2, '牛子', comment='2 查信息，没有成就')
    wrap(user_2, 'pk', at_qq=user_1, comment='2 pk 1 第一次')
    wrap(user_2, 'pk', at_qq=user_1, comment='2 pk 1 第二次，获取成就')

    wrap(user_2, '牛子成就', comment='2 查成就')
    wrap(user_2, '牛子', comment='2 查信息，有成就')
    wrap(user_2, '牛子排名', comment='2 查排名')

    # 模拟 user 3 一下子获得两个成就
    wrap(user_3, '注册牛子', comment='3 注册')
    wrap(user_3, '牛子成就', comment='3 查成就，没有东西')
    user_3_badge_data = Sql.sub_table_badge.select_single_data(user_3)
    user_3_badge_data['pk_win_count'] = 50
    user_3_badge_data['pk_plus_length_total'] = 50
    user_3_badge_data['glue_plus_count'] = 50
    user_3_badge_data['glue_plus_length_total'] = 150
    Sql.sub_table_badge.update_single_data(user_3_badge_data)
    wrap(user_3, '牛子', comment='3 查信息，此时获得了成就')
    wrap(user_3, '牛子成就', comment='3 查成就')
    wrap(user_3, '牛子排名', comment='3 查排名')

    # 检验加权生效
    data = DB.load_data(user_3)
    data['length'] = 500
    DB.write_data(data)
    wrap(user_3, 'pk', at_qq=user_1, comment='3 pk 1 有加权')
    wrap(user_3, '打胶', at_qq=user_1, comment='3 打胶 1 有加权')

# https://github.com/opq-osc/chinchin-pk/pull/4
def pull_4():

    wrap(user_1, '注册牛子', comment='1 注册')
    wrap(user_2, '注册牛子', comment='2 注册')
    wrap(user_3, '注册牛子', comment='3 注册')

    # delete 2 and 3 badge data for simulate incremental update
    Sql.sub_table_badge.delete_single_data(user_2)
    Sql.sub_table_badge.delete_single_data(user_3)

    wrap(user_1, '牛子排名', comment='1 查排名')
    wrap(user_1, '看他牛子', at_qq=user_2, comment='1 查看 2 牛子')
    wrap(user_1, '看他牛子', at_qq=user_3, comment='1 查看 3 牛子')

def test_farm():

    wrap(user_1, '注册牛子', comment='1 注册')
    wrap(user_2, '注册牛子', comment='2 注册')

    # 查仙境信息
    wrap(user_1, '牛子仙境', comment='1 查仙境信息')

    # 开始修炼
    # 不允许修炼
    config = FarmSystem.read_farm_config()
    config['can_play_time']['duration'] = { 'h': 0, 'm': 0 }
    FarmSystem.modify_config_in_runtime(config)
    wrap(user_1, '牛子修炼', comment='1 开始修炼，不在时间内没法修炼')

    # 可以修炼的时间
    config = FarmSystem.read_farm_config()
    config['can_play_time']['start'] = "00:00"
    config['can_play_time']['duration'] = { 'h': 24, 'm': 0 }
    FarmSystem.modify_config_in_runtime(config)
    wrap(user_1, '牛子练功', comment='1 开始修炼')
    wrap(user_1, '牛子修仙', comment='1 修炼别名，无法继续')
    wrap(user_1, '打胶', comment='1 在修炼，无法操作')
    wrap(user_1, '🔒我', comment='1 在修炼，无法操作')
    wrap(user_1, '🔒', user_2, comment='1 在修炼，无法操作')
    wrap(user_1, 'pk', user_2, comment='1 在修炼，无法操作')
    wrap(user_1, '打胶', user_2, comment='1 在修炼，无法操作')
    wrap(user_1, '牛子转生', comment='1 在修炼，无法操作')
    # 可以查
    wrap(user_1, '牛子', comment='1 查信息，可以')
    wrap(user_1, '牛子成就', comment='1 查成就，可以')
    wrap(user_1, '牛子排名', comment='1 查排名，可以')
    wrap(user_1, '牛子仙境', comment='1 查仙境，可以')

    # 修炼阶段改变
    data = DB.sub_db_farm.get_user_data(user_1)
    now = ArrowUtil.get_now_time()
    data['farm_latest_plant_time'] = ArrowUtil.get_time_with_shift(
        now, shift_mins=(-1 * 60 * 4)
    )
    DB.sub_db_farm.update_user_data(data)
    wrap(user_1, '牛子仙境', comment='1 查仙境，阶段变了')

    # 修炼完了
    data = DB.sub_db_farm.get_user_data(user_1)
    now = ArrowUtil.get_now_time()
    data['farm_latest_plant_time'] = ArrowUtil.get_time_with_shift(
        now, shift_mins=(-1 * 60 * 5) - 1
    )
    DB.sub_db_farm.update_user_data(data)
    wrap(user_1, 'pk', user_2, comment='1 pk，可以活动了，并且修炼结束')
    wrap(user_1, '牛子仙境', comment='1 查仙境，修炼结束')
    wrap(user_1, '牛子', comment='1 查牛子信息')

    # 再修炼一次
    wrap(user_1, '牛子修炼', comment='1 开始修炼')
    wrap(user_2, '牛子修炼', comment='2 开始修炼')
    wrap(user_1, '牛子仙境', comment='1 查仙境')

    # 修炼时间结束了
    config = FarmSystem.read_farm_config()
    config['can_play_time']['duration'] = { 'h': 0, 'm': 0 }
    FarmSystem.modify_config_in_runtime(config)
    wrap(user_1, '牛子修炼', comment='1 反复修炼，但修炼时间结束了')


def test_friends():

    wrap(user_1, '注册牛子', comment='1 注册')
    wrap(user_2, '注册牛子', comment='2 注册')
    wrap(user_3, '注册牛子', comment='3 注册')

    # 查看好友
    wrap(user_1, '牛友', comment='1 查看好友，没朋友')

    # 模拟增量
    Sql.sub_table_friends.delete_single_data(user_2)

    # 交朋友
    wrap(user_1, '关注牛子', comment='1 和 空气 交朋友，没反应')
    data = DB.load_data(user_1)
    data['length'] = 0.9
    DB.write_data(data)
    data2 = DB.load_data(user_2)
    data2['length'] = 100 # 预计需要 1cm 朋友费
    DB.write_data(data2)
    wrap(user_1, '关注牛子', user_2, comment='1 和 2 交朋友，没钱，交不起')
    data = DB.load_data(user_1)
    data['length'] = 1
    DB.write_data(data)
    wrap(user_1, '关注牛子', user_2, comment='1 和 2 交朋友，有钱，交朋友成功')
    wrap(user_1, '牛子', comment='1 查信息，自己没牛子了')
    wrap(user_1, '牛友', comment='1 查看好友，有朋友了')

    # 2 看自己资产多了
    wrap(user_2, '牛子', comment='2 查信息，长度收到了 0.8 ，扣了 20% 手续费')

    # 友尽掉 2
    wrap(user_1, '取关牛子', user_2, comment='1 友尽 2')
    wrap(user_1, '牛友', comment='1 查看好友，没朋友了')
    # 数据正确性
    data2 = DB.sub_db_friends.get_user_data(user_2)
    assert data2['friends_share_count'] == 0
    assert data2['friends_list'] == ''

    # 1 继续交 2 
    data = DB.load_data(user_1)
    data['length'] = 10
    DB.write_data(data)
    wrap(user_1, '关注牛子', user_2, comment='1 和 2 交朋友，有钱，交朋友成功')
    wrap(user_2, '牛子', comment='2 查信息，第一笔账收到了')
    wrap(user_1, '牛友', comment='1 查看好友，有朋友了，朋友费涨到 1.12，因为 2 的长度收了一次费用')
    # 数据正确性
    data2 = DB.load_data(user_2)
    assert data2['length'] == 101.61
    expect_friends_cost = data2['length'] * 0.011
    assert fixed_two_decimal_digits(expect_friends_cost, to_number=True) == 1.12
    wrap(user_2, '牛子', comment='2 查信息')
    # 隔日
    yesterday = ArrowUtil.get_time_with_shift(
        ArrowUtil.get_now_time(), shift_days=-1
    )
    def jump_day(day: str):
        data = DB.sub_db_friends.get_user_data(user_1)
        data['friends_cost_latest_time'] = day
        DB.sub_db_friends.update_user_data(data)
        data = DB.sub_db_friends.get_user_data(user_2)
        data['friends_cost_latest_time'] = day
        DB.sub_db_friends.update_user_data(data)

    # 假设过了一天
    jump_day(yesterday)

    # 1 只有支出，没有收入
    # 2 只有收入，没有支出
    data = DB.load_data(user_1)
    data['length'] = 10
    DB.write_data(data)
    data2 = DB.load_data(user_2)
    data2['length'] = 100 # 预计收到 100 * 0.011 = 1.1cm 朋友费，扣掉 20% 手续费，收到 0.88cm
    DB.write_data(data2)
    wrap(user_1, '牛子', user_2, comment='1 隔日，自己付了 1.1')
    wrap(user_2, '牛子', comment='2 隔日，自己收了 0.88')
    # 数据正确性
    data = DB.load_data(user_1)
    assert data['length'] == 8.90 # 付了 1.1
    data2 = DB.load_data(user_2)
    assert data2['length'] == 100.88 # 100 + 0.88

    # 有收入，有支出
    wrap(user_2, '关注牛子', user_1, comment='2 关注 1')
    wrap(user_2, '牛友', comment='2 查朋友列表')
    wrap(user_1, '牛友', comment='1 查朋友列表，现在双向关系')
    data = DB.load_data(user_1)
    data['length'] = 10 # 预计收到 10 * 0.011 = 0.11cm 朋友费，扣掉 20% 手续费，收到 0.088cm
    DB.write_data(data)
    data2 = DB.load_data(user_2)
    data2['length'] = 100 # 预计收到 0.88 朋友费
    DB.write_data(data2)
    # 隔日
    jump_day(yesterday)
    # 天亮了
    wrap(user_1, '牛子', comment='1 隔日，付了 1.1，没收钱，因为 2 没说话，2 没结算')
    wrap(user_2, '牛子', comment='2 隔日，付了 0.11 ，收了 0.88')
    wrap(user_1, '牛友', comment='1 查牛友，不会有多余的消息了')
    # 隔日
    jump_day(yesterday)
    wrap(user_2, '牛子', comment='2 再隔日，只有支出，没有收入，因为 1 没结算')
    wrap(user_1, '牛子', comment='1 再隔日，结算 昨天+今天的 2 的朋友费')

    # 清空关系
    wrap(user_1, '取关牛子', user_2, comment='1 取关 2')
    wrap(user_2, '取关牛子', user_1, comment='2 取关 1 ，2 还有一笔结算要明天进行')

    # 手续费
    # pass ，前文 case 已经覆盖

    # 最大值
    def modify_max(max: int):
        config = FriendsSystem.read_config()
        config['max'] = max
        FriendsSystem.modify_config_in_runtime(config)
    modify_max(0)
    wrap(user_1, '关注牛子', user_2, comment='1 和 2 交，没法交，到达上线了')

    # 间隔多日
    before_yesterday = ArrowUtil.get_time_with_shift(
        ArrowUtil.get_now_time(), shift_days=-2
    )
    modify_max(1)
    wrap(user_1, '关注牛子', user_2, comment='1 和 2 交')
    wrap(user_2, '关注牛子', user_1, comment='2 和 1 交，昨天的结算了')
    wrap(user_1, '牛子好友', comment='1 查好友列表，看看多少费用')
    # 跳 2 天
    jump_day(before_yesterday)
    wrap(user_1, '牛子', comment='1 隔 2 日，需要付 2 倍')
    wrap(user_2, '牛子', comment='2 隔 2 日')

    # 多人测试
    wrap(user_1, '关注牛子', user_3, comment='1 和 3 交，max 了')
    modify_max(2)
    wrap(user_1, '关注牛子', user_3, comment='1 和 3 交')
    wrap(user_2, '关注牛子', user_3, comment='2 和 3 交')

    wrap(user_1, '牛子好友', comment='1 查好友列表')
    wrap(user_2, '牛子好友', comment='2 查好友列表')
    wrap(user_3, '牛子好友', comment='3 查好友列表')

    # 隔日
    jump_day(yesterday)
    wrap(user_1, '牛子', comment='1 隔日')
    wrap(user_2, '牛子', comment='2 隔日')
    wrap(user_3, '牛子', comment='3 隔日')

    # 自动友尽
    data3 = DB.load_data(user_3)
    data3['length'] = 1000
    DB.write_data(data3)
    # 隔日
    jump_day(yesterday)
    wrap(user_1, '牛子', comment='1 隔日，自动友尽')
    wrap(user_2, '牛子', comment='2 隔日，自动友尽')
    wrap(user_3, '牛子', comment='3 隔日，自动友尽')

    # 自动多人友尽
    modify_max(6)
    wrap(user_1, '关注牛子', user_3, comment='1 和 3 交，不成功，没钱')
    data = DB.load_data(user_1)
    data['length'] = 20
    DB.write_data(data)
    data2 = DB.load_data(user_2)
    data2['length'] = 1000
    DB.write_data(data2)
    wrap(user_1, '关注牛子', user_3, comment='1 和 3 交，成功')
    # 隔日，自动断绝 2 和 3
    jump_day(yesterday)
    wrap(user_1, '牛子', comment='1 隔日，自动断绝 2 和 3')
    wrap(user_2, '牛子', comment='2 隔日，自动断绝 2 和 3')
    wrap(user_3, '牛子', comment='3 隔日，自动断绝 2 和 3')

    # ...

if __name__ == '__main__':
    clear_database()

    # args: --legacy
    if arg('--legacy'):
        test_legacy()

    # args: --nickname
    if arg('--nickname'):
        test_nickname()

    # args: --rebirth
    if arg('--rebirth'):
        test_rebirth()

    # args: --badge
    if arg('--badge'):
        test_badge()
    
    # args: --pull-4
    if arg('--pull-4'):
        pull_4()

    # args: --farm
    if arg('--farm'):
        test_farm()

    # args: --friends
    if arg('--friends'):
        test_friends()

    # clear log
    if arg('--clear'):
        clear_logger()

    # write_snapshot()
