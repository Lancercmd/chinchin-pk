import arrow


def join(arr: list, sep: str = ''):
    # filter all empty value
    arr = list(filter(lambda x: x, arr))
    return sep.join(arr)


def get_now_time():
    return arrow.now().format('YYYY-MM-DD HH:mm:ss')


def date_improve(time: str):
    ins = arrow.get(time)
    is_today = (ins.format('YYYY-MM-DD') == arrow.now().format('YYYY-MM-DD'))
    if is_today:
        return ins.format('HH:mm')
    is_this_year = (ins.format('YYYY') == arrow.now().format('YYYY'))
    if is_this_year:
        return ins.format('MM-DD HH:mm')
    return ins.format('YYYY-MM-DD HH:mm')


def fixed_two_decimal_digits(num: int, to_number: bool = False):
    result = '{:.2f}'.format(num)
    if to_number:
        return float(result)
    return result


def is_date_outed(time: str):
    return arrow.get(time).format('YYYY-MM-DD') != arrow.now().format('YYYY-MM-DD')


def create_match_func_factory(message: str, fuzzy: bool = False):
    def is_keyword_matched(keywords: list, text: str):
        for keyword in keywords:
            if fuzzy:
                if text.startswith(keyword):
                    return True
            else:
                if text == keyword:
                    return True
        return False
    return is_keyword_matched
