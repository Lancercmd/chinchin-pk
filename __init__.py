from botoy import GroupMsg, S
from botoy import async_decorators as deco
from botoy import jconfig, logger
from botoy.collection import MsgTypes
from botoy.parser import group as gp

from .src.main import message_processor, KEYWORDS
from .src.utils import get_object_values, create_match_func_factory

__doc__ = "牛子系统"
config = jconfig.get_configuration("chinchin_system")
groups = config.get("groups")

logger.info(f"{__doc__}:监听群组:{groups}")

keywords = get_object_values(KEYWORDS)
match_func = create_match_func_factory(fuzzy=True)

@deco.ignore_botself
@deco.from_these_groups(*groups)
async def receive_group_msg(ctx: GroupMsg):
    from_user = ctx.FromUserId
    content = ctx.Content
    group = ctx.FromGroupId

    if ctx.MsgType == MsgTypes.PicMsg:
        return

    if not match_func(keywords=keywords, text=content):
        return
        
    def impl_at_segment(qq: int):
        return ctx.FromNickName

    def impl_send_message(qq: int, group: int, message: str):
        S.bind(ctx).text(message)
        return

    at_data = gp.at(ctx)
    if at_data:
        # 只对 at 一个人生效
        if len(at_data.UserExt[0]) != 1:
            return
        target = at_data.UserExt[0].QQUid
        message_processor(
            message=content,
            qq=from_user,
            at_qq=target,
            group=group,
            fuzzy_match=True,
            impl_at_segment=impl_at_segment,
            impl_send_message=impl_send_message
        )
        return
    elif ctx.MsgType == MsgTypes.TextMsg:
        message_processor(
            message=content,
            qq=from_user,
            group=group,
            fuzzy_match=True,
            impl_at_segment=impl_at_segment,
            impl_send_message=impl_send_message
        )
        return
