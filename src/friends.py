from .config import Config
from .db import DB
from .utils import fixed_two_decimal_digits, ArrowUtil

global cache


class FriendsSystem():

    @staticmethod
    def read_config():
        global cache
        if cache:
            return cache
        json = Config.get_config('friends')
        cache = json
        return cache

    @staticmethod
    def get_friends_data(qq: int):
        data = DB.sub_db_friends.get_user_data(qq)
        friends = []
        # parse string to int list
        friends_list = data['friends_list'].split(',')
        for friend in friends_list:
            qq_int = int(friend)
            friends.append(qq_int)
        data['friends_list'] = friends
        # search user data and merge
        user_data = DB.load_data(qq)
        merge = DB.utils.merge_data(user_data, data)
        return merge

    @classmethod
    def get_batch_friends_info_by_qqs(cls, qqs: list):
        config = cls.read_config()
        friends_data = DB.sub_db_friends.get_batch_user_data(qqs)
        users_data = DB.get_batch_users(qqs)
        info_table_data = DB.sub_db_info.get_batch_user_infos(qqs)
        merge = DB.utils.merge_data_list(
            [users_data, info_table_data, friends_data],
        )
        infos = []
        for user in merge:
            base_friend_cost = config['cost']['base'] * user['length']
            share_friend_cost = config['cost']['share'] * \
                user['friends_share_count']
            total_cost = fixed_two_decimal_digits(
                base_friend_cost + share_friend_cost, to_number=True)
            info = {
                'friends_need_cost': total_cost,
                **user,
            }
            infos.append(info)
        # sort by cost
        infos = sorted(infos, key=lambda x: x['friends_need_cost'])
        return infos

    @classmethod
    def get_friends_list_view(cls, qq: int):
        friends_data = cls.get_friends_data(qq)
        friends_list = friends_data['friends_list']
        is_not_has_friends = len(friends_list) == 0
        if is_not_has_friends:
            message_arr = ['相比之下，你就是个没有朋友的土地瓜。']
            return '\n'.join(message_arr)
        # has friends, show list
        message_arr = [
            '【牛友列表】',
        ]
        # search friends info
        infos = cls.get_batch_friends_info_by_qqs(friends_list)
        for info in infos:
            index = friends_list.index(info)
            nickname = info.get('latest_speech_nickname', '无名英雄')
            cost_daily = info['friends_need_cost']
            share_count = info['friends_share_count']
            message_arr.append(
                f'{index + 1}. {nickname} ({share_count}人共享、朋友费{cost_daily}cm)'
            )
        return '\n'.join(message_arr)

    @classmethod
    def add_friends(cls, qq: int, target_qq: int):
        # add friend to qq
        data = DB.sub_db_friends.get_user_data(qq)
        friends_list = data['friends_list'].split(',')
        is_in_list = str(target_qq) in friends_list
        if not is_in_list:
            friends_list.append(str(target_qq))
        data['friends_list'] = ','.join(friends_list)
        # update pay time
        data['friends_cost_latest_time'] = ArrowUtil.get_now_time()
        DB.sub_db_friends.update_user_data(qq, data)
        # add share count to target_qq
        target_data = DB.sub_db_friends.get_user_data(target_qq)
        target_data['friends_share_count'] += 1
        DB.sub_db_friends.update_user_data(target_qq, target_data)

    @classmethod
    def delete_friends(cls, qq: int, target_qq: int):
        # remove target from qq
        data = DB.sub_db_friends.get_user_data(qq)
        friends_list = data['friends_list'].split(',')
        is_in_list = str(target_qq) in friends_list
        if is_in_list:
            friends_list.remove(str(target_qq))
        data['friends_list'] = ','.join(friends_list)
        DB.sub_db_friends.update_user_data(qq, data)
        # remove share count from target_qq
        target_data = DB.sub_db_friends.get_user_data(target_qq)
        target_data['friends_share_count'] -= 1
        DB.sub_db_friends.update_user_data(target_qq, target_data)

    @classmethod
    def transfer_length(cls, target_qq: int, origin_length: float):
        config = cls.read_config()
        fee = config['fee']['friends']
        # transfer length to target
        will_transfer_length = origin_length * (1 - fee)
        data = DB.sub_db_friends.get_user_data(target_qq)
        data['friends_will_collect_length'] += will_transfer_length
        DB.sub_db_friends.update_user_data(target_qq, data)

    @classmethod
    def check_friends_daily(cls, qq: int):
        """
          注意朋友如果不上线（说话），长度不会自动转账，可以一直不说话跑路，上线那一天才会转账或友尽
        """
        friends_data = cls.get_friends_data(qq)
        is_has_friends = len(friends_data['friends_list']) > 0
        if not is_has_friends:
            return None
        # check friends cost
        latest_pay_time = friends_data['friends_cost_latest_time']
        is_need_pay = ArrowUtil.is_date_outed(
            latest_pay_time)
        if not is_need_pay:
            return None
        else:
            # need pay
            infos = cls.get_batch_friends_info_by_qqs(
                friends_data['friends_list'])
            # 收款额
            will_get_length = fixed_two_decimal_digits(
                friends_data['friends_will_collect_length'], to_number=True)
            origin_length = friends_data['length'] + will_get_length
            current_has_length = origin_length
            can_keep_friends_list = []
            friends_over_list = []
            # gap days
            now = ArrowUtil.get_now_time()
            gap_days = ArrowUtil.get_time_diff_days(
                latest_pay_time, now
            )
            # 由大到小支付
            for info in infos:
                need_pay_length = gap_days * info['friends_need_cost']
                if current_has_length >= need_pay_length:
                    # can keep
                    can_keep_friends_list.append(info)
                    current_has_length -= need_pay_length
                else:
                    # over
                    friends_over_list.append(info)
            total_need_cost_length = fixed_two_decimal_digits(
                origin_length - current_has_length, to_number=True)
            message_arr = [
                f'今日朋友费支出{total_need_cost_length}cm，收入{will_get_length}cm，好幸福。',
            ]
            profit = fixed_two_decimal_digits(
                will_get_length - total_need_cost_length, to_number=True)
            # batch pay to every friend
            for info in can_keep_friends_list:
                cls.transfer_length(info['qq'], info['friends_need_cost'])
            has_over_friends = len(friends_over_list) > 0
            if has_over_friends:
                first_over_friend = friends_over_list[0]
                nickname = first_over_friend.get(
                    'latest_speech_nickname', '无名英雄')
                numbers = len(friends_over_list)
                over_text = None
                if numbers == 1:
                    over_text = f'{nickname}已取关你！'
                else:
                    over_text = f'{nickname}等{numbers}人已取关你！'
                message_arr.append(
                    f'“今天的朋友费...”，“土地瓜，还想白嫖我”，因为你付不起朋友费，{over_text}')
                # batch delete friends
                for info in friends_over_list:
                    cls.delete_friends(qq, info['qq'])
            # update latest pay time
            friends_data['friends_cost_latest_time'] = ArrowUtil.get_now_time()
            # clear friends_will_collect_length
            friends_data['friends_will_collect_length'] = 0
            # update latest collect time: 这个字段还没什么用，先保留着吧
            friends_data['friends_collect_latest_time'] = ArrowUtil.get_now_time()
            DB.sub_db_friends.update_user_data(qq, friends_data)
            return {
                'message': '\n'.join(message_arr),
                'profit': profit,  # > 0 or < 0
            }
