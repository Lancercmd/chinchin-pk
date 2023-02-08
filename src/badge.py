from .config import Config
from .db import DB

cache = None


class BadgeSystem():

    @staticmethod
    def get_badge_configs():
        global cache
        if cache is None:
            configs = Config.get_config('badge')['categories']
            # make level to value map
            map = {}
            for config in configs:
                map[config['level']] = config['value']
            cache = map
        return cache

    @classmethod
    def get_badge_by_qq(cls, qq: int):
        badge_data = DB.sub_db_badge.get_badge_data(qq)
        ids_str_arr = badge_data.get('badge_ids', '').split(',')
        if not ids_str_arr:
            return []
        ids = [int(i) for i in ids_str_arr if i]
        configs = cls.get_badge_configs()
        badge_arr = []
        for id in ids:
            badge_arr.append(configs[id])
        # sort bt priority desc
        badge_arr.sort(key=lambda x: x['priority'], reverse=True)
        return badge_arr

    @classmethod
    def get_badge_label_by_qq(cls, qq: int):
        badge_arr = cls.get_badge_by_qq(qq)
        if not badge_arr:
            return None
        badge_names = [i['name'] for i in badge_arr]
        return ' · '.join(badge_names)

    @classmethod
    def get_first_badge_by_badge_string_arr(cls, bade_ids: str = None):
        """
          "1,2,3" -> "xxx"
        """
        if not bade_ids:
            return None
        ids_str_arr = bade_ids.split(',')
        ids = [int(i) for i in ids_str_arr if i]
        configs = cls.get_badge_configs()
        max_priority_badge = None
        for id in ids:
            badge = configs[id]
            if (max_priority_badge is None) or (badge['priority'] > max_priority_badge['priority']):
                max_priority_badge = badge
        return max_priority_badge['name']

    @staticmethod
    def get_badge_view(cls, qq: int):
        badge_arr = cls.get_badge_by_qq(qq)
        if not badge_arr:
            return None
        arr = []
        for badge in badge_arr:
            index = badge_arr.index(badge)
            arr.append(
                f"{index + 1}. 【{badge['name']}】 {badge['description']}")
        return '\n'.join(arr)
