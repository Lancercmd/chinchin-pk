import db
import impl
import utils
from typing import Optional
import config

KEYWORDS = {
    'chinchin': '牛子',
    'pk': 'pk',
    'lock_me': '🔒我',
    'lock': '🔒',
    'glue': '打胶'
}

DEFAULT_NONE_TIME = '2000-01-01 00:00:00'


def message_processor(message: str, qq: int, group: int, at_qq: Optional[int] = None):
    """
        main entry
        TODO：打胶 cd
        TODO: 看别人牛子（ e.g. 看他牛子 @user )
    """
    message = message.strip()

    # 查询牛子信息
    if message == KEYWORDS.get('chinchin'):
        return entry_chinchin(qq, group)

    # 下面的逻辑必须有牛子
    if not db.is_registered(qq):
        message_arr = [
            impl.get_at_segment(qq),
            '你还没有牛子！'
        ]
        impl.send_message(qq, group,
                          utils.join(message_arr, '\n')
                          )
        return

    # 对别人的
    if at_qq:
        if not db.is_registered(at_qq):
            message_arr = [
                impl.get_at_segment(qq),
                '对方还没有牛子！'
            ]
            impl.send_message(qq, group,
                              utils.join(message_arr, '\n')
                              )
            return

        # pk别人
        if message == KEYWORDS.get('pk'):
            return entry_pk_with_target(qq, group, at_qq)

        # 🔒别人
        if message == KEYWORDS.get('lock'):
            return entry_lock_with_target(qq, group, at_qq)

        # 打胶别人
        if message == KEYWORDS.get('glue'):
            return entry_glue_with_target(qq, group, at_qq)
    else:
        # 🔒自己
        if message == KEYWORDS.get('lock_me'):
            return entry_lock_me(qq, group)

        # 自己打胶
        if message == KEYWORDS.get('glue'):
            return entry_glue(qq, group)


def entry_chinchin(qq: int, group: int):
    if db.is_registered(qq):
        user_data = db.load_data(qq)
        message_arr = [
            impl.get_at_segment(qq),
            '【牛子信息】',
        ]
        # length
        message_arr.append(
            '长度: {}厘米'.format(utils.fixed_two_decimal_digits(
                user_data.get('length'),
                to_number=False
            ))
        )
        # locked
        if user_data.get('locked_time') != DEFAULT_NONE_TIME:
            message_arr.append(
                '最近被🔒时间: {}'.format(
                    utils.date_improve(
                        user_data.get('locked_time')
                    )
                )
            )
        # pk
        if user_data.get('pk_time') != DEFAULT_NONE_TIME:
            message_arr.append(
                '最近pk时间: {}'.format(
                    utils.date_improve(
                        user_data.get('pk_time')
                    )
                )
            )
        # pked
        if user_data.get('pked_time') != DEFAULT_NONE_TIME:
            message_arr.append(
                '最近被pk时间: {}'.format(
                    utils.date_improve(
                        user_data.get('pked_time')
                    )
                )
            )
        # glueing
        if user_data.get('glueing_time') != DEFAULT_NONE_TIME:
            message_arr.append(
                '最近打胶时间: {}'.format(
                    utils.date_improve(
                        user_data.get('glueing_time')
                    )
                )
            )
        # glued
        if user_data.get('glued_time') != DEFAULT_NONE_TIME:
            message_arr.append(
                '最近被打胶时间: {}'.format(
                    utils.date_improve(
                        user_data.get('glued_time')
                    )
                )
            )
        # register
        message_arr.append(
            '注册时间: {}'.format(utils.date_improve(
                user_data.get('register_time')
            ))
        )
        impl.send_message(
            qq, group,
            utils.join(message_arr, '\n')
        )
    else:
        new_user = {
            'qq': qq,
            'length': config.new_chinchin_length(),
            'register_time': utils.get_now_time(),
            'daily_lock_count': 0,
            'daily_pk_count': 0,
            'daily_glue_count': 0,
            'latest_daily_lock': DEFAULT_NONE_TIME,
            'latest_daily_pk': DEFAULT_NONE_TIME,
            'latest_daily_glue': DEFAULT_NONE_TIME,
            'pk_time': DEFAULT_NONE_TIME,
            'pked_time': DEFAULT_NONE_TIME,
            'glueing_time': DEFAULT_NONE_TIME,
            'glued_time': DEFAULT_NONE_TIME,
            'locked_time': DEFAULT_NONE_TIME,
        }
        db.create_data(qq, new_user)


def entry_lock_me(qq: int, group: int):
    # FIXME: 如果自己被🔒到当日上限，自己就不能🔒自己了，但自己🔒自己的条件也高。
    #        因为🔒自己回报高，这样会导致强者一直🔒自己，越强，所以还需要一种小概率制裁机制。
    # check limited
    is_today_limited = db.is_lock_daily_limited(qq)
    if is_today_limited:
        message_arr = [
            impl.get_at_segment(qq),
            '你的牛子今天太累了，改天再来吧！'
        ]
        impl.send_message(qq, group,
                          utils.join(message_arr, '\n')
                          )
        return
    lock_me_min = config.get_config('lock_me_chinchin_min')
    user_data = db.load_data(qq)
    db.record_time(qq, 'locked_time')
    db.count_lock_daily(qq)
    if user_data.get('length') < lock_me_min:
        is_need_punish = config.is_hit('lock_me_negative_prob')
        if is_need_punish:
            punish_value = config.get_lock_me_punish_value()
            db.length_decrease(qq, punish_value)
            message_arr = [
                impl.get_at_segment(qq),
                '你的牛子还不够长，你🔒不着，牛子自尊心受到了伤害，缩短了{}厘米'.format(punish_value)
            ]
            impl.send_message(qq, group,
                              utils.join(message_arr, '\n')
                              )
        else:
            message_arr = [
                impl.get_at_segment(qq),
                '你的牛子太小了，还🔒不到'
            ]
            impl.send_message(qq, group,
                              utils.join(message_arr, '\n')
                              )
    else:
        is_lock_failed = config.is_hit(
            'lock_me_negative_prob_with_strong_person')
        if is_lock_failed:
            punish_value = config.get_lock_punish_with_strong_person_value()
            db.length_decrease(qq, punish_value)
            message_arr = [
                impl.get_at_segment(qq),
                '你的牛子太长了，没🔒住爆炸了，缩短了{}厘米'.format(punish_value)
            ]
            impl.send_message(qq, group,
                              utils.join(message_arr, '\n')
                              )
        else:
            plus_value = config.get_lock_plus_value()
            db.length_increase(qq, plus_value)
            # TODO: 🔒自己效果有加成
            message_arr = [
                impl.get_at_segment(qq),
                '🔒的很卖力很舒服，你的牛子增加了{}厘米'.format(plus_value)
            ]
            impl.send_message(qq, group,
                              utils.join(message_arr, '\n')
                              )


def entry_glue(qq: int, group: int):
    # check limited
    is_today_limited = db.is_glue_daily_limited(qq)
    if is_today_limited:
        message_arr = [
            impl.get_at_segment(qq),
            '牛子快被你冲炸了，改天再来冲吧！'
        ]
        impl.send_message(qq, group,
                          utils.join(message_arr, '\n')
                          )
        return
    db.record_time(qq, 'glueing_time')
    db.count_glue_daily(qq)
    is_glue_failed = config.is_hit('glue_self_negative_prob')
    if is_glue_failed:
        punish_value = config.get_glue_self_punish_value()
        db.length_decrease(qq, punish_value)
        message_arr = [
            impl.get_at_segment(qq),
            '打胶结束，牛子快被冲爆炸了，减小{}厘米'.format(punish_value)
        ]
        impl.send_message(qq, group,
                          utils.join(message_arr, '\n')
                          )
    else:
        plus_value = config.get_glue_plus_value()
        db.length_increase(qq, plus_value)
        message_arr = [
            impl.get_at_segment(qq),
            '牛子对你的付出很满意吗，增加{}厘米'.format(plus_value)
        ]
        impl.send_message(qq, group,
                          utils.join(message_arr, '\n')
                          )


def entry_pk_with_target(qq: int, group: int, at_qq: int):
    # 不能 pk 自己
    if qq == at_qq:
        message_arr = [
            impl.get_at_segment(qq),
            '你不能和自己的牛子进行较量！'
        ]
        impl.send_message(qq, group,
                          utils.join(message_arr, '\n')
                          )
        return
    # check limited
    is_today_limited = db.is_pk_daily_limited(qq)
    if is_today_limited:
        message_arr = [
            impl.get_at_segment(qq),
            '牛子刚结束战斗，歇一会吧！'
        ]
        impl.send_message(qq, group,
                          utils.join(message_arr, '\n')
                          )
        return
    target_data = db.load_data(at_qq)
    user_data = db.load_data(qq)
    target_length = target_data.get('length')
    user_length = user_data.get('length')
    offset = user_length - target_length
    offset_abs = abs(offset)
    is_user_win = False
    if offset_abs < config.get_config('pk_unstable_range'):
        is_user_win = config.is_pk_win()
    else:
        is_user_win = (offset > 0)
    db.record_time(qq, 'pk_time')
    db.record_time(at_qq, 'pked_time')
    db.count_pk_daily(qq)
    if is_user_win:
        user_plus_value = config.get_pk_plus_value()
        target_punish_value = config.get_pk_punish_value()
        db.length_increase(qq, user_plus_value)
        db.length_decrease(at_qq, target_punish_value)
        message_arr = [
            impl.get_at_segment(qq),
            'pk成功了，对面牛子不值一提，你的是最棒的，牛子获得自信增加了{}厘米，对面牛子减小了{}厘米'.format(
                user_plus_value, target_punish_value)
        ]
        impl.send_message(qq, group,
                          utils.join(message_arr, '\n')
                          )
    else:
        user_punish_value = config.get_pk_punish_value()
        target_plus_value = config.get_pk_plus_value()
        db.length_decrease(qq, user_punish_value)
        db.length_increase(at_qq, target_plus_value)
        message_arr = [
            impl.get_at_segment(qq),
            'pk失败了，在对面牛子的阴影笼罩下，你的牛子减小了{}厘米，对面牛子增加了{}厘米'.format(
                user_punish_value, target_plus_value)
        ]
        impl.send_message(qq, group,
                          utils.join(message_arr, '\n')
                          )


def entry_lock_with_target(qq: int, group: int, at_qq: int):
    # 🔒 自己是单独的逻辑
    if qq == at_qq:
        entry_lock_me(qq, group)
        return
    # TODO：🔒别人可能失败
    # check limited
    is_today_limited = db.is_lock_daily_limited(qq)
    if is_today_limited:
        message_arr = [
            impl.get_at_segment(qq),
            '别🔒了，要口腔溃疡了，改天再🔒吧！'
        ]
        impl.send_message(qq, group,
                          utils.join(message_arr, '\n')
                          )
        return
    target_plus_value = config.get_lock_plus_value()
    db.length_increase(at_qq, target_plus_value)
    db.record_time(at_qq, 'locked_time')
    db.count_lock_daily(qq)
    message_arr = [
        impl.get_at_segment(qq),
        '🔒的很卖力很舒服，对方牛子增加了{}厘米'.format(target_plus_value)
    ]
    impl.send_message(qq, group,
                      utils.join(message_arr, '\n')
                      )


def entry_glue_with_target(qq: int, group: int, at_qq: int):
    # 打胶自己跳转
    if qq == at_qq:
        entry_glue(qq, group)
        return
    # check limited
    is_today_limited = db.is_glue_daily_limited(qq)
    if is_today_limited:
        message_arr = [
            impl.get_at_segment(qq),
            '你刚打了一胶，歇一会吧！'
        ]
        impl.send_message(qq, group,
                          utils.join(message_arr, '\n')
                          )
        return
    db.record_time(at_qq, 'glued_time')
    db.count_glue_daily(qq)
    is_glue_failed = config.is_hit('glue_negative_prob')
    if is_glue_failed:
        target_punish_value = config.get_glue_punish_value()
        db.length_decrease(at_qq, target_punish_value)
        message_arr = [
            impl.get_at_segment(qq),
            '对方牛子快被大家冲坏了，减小{}厘米'.format(target_punish_value)
        ]
        impl.send_message(qq, group,
                          utils.join(message_arr, '\n')
                          )
    else:
        target_plus_value = config.get_glue_plus_value()
        db.length_increase(at_qq, target_plus_value)
        message_arr = [
            impl.get_at_segment(qq),
            '你的打胶让对方牛子感到很舒服，对方牛子增加{}厘米'.format(target_plus_value)
        ]
        impl.send_message(qq, group,
                          utils.join(message_arr, '\n')
                          )
