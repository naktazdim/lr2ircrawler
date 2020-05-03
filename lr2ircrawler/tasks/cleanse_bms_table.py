"""
http://bmsnormal2.syuriken.jp/bms_dtmanager.html
"""

from typing import List

from more_itertools import unique_everseen


def get_level_order(bms_table: dict) -> List[str]:
    """
    表データからレベル順を得る。

    :param bms_table: 表データ
    :return: level_order
    """
    # ひとまずデータ部に出現するレベルを出現順に列挙
    level_order_from_data = list(unique_everseen([chart["level"] for chart in bms_table["data"]]))

    # ヘッダ部にlevel_orderの指定がなかったら、データ部から得たレベル順をそのまま使う (仕様)
    if "level_order" not in bms_table["header"]:
        return level_order_from_data

    # ヘッダ部にlevel_orderの指定があったらそれを使う (仕様)
    level_order = bms_table["header"]["level_order"]

    # のだが、データ部との不整合が起こらないように以下のような処理を行っておく (独自解釈)
    level_order = map(str, level_order)  # データ部に合わせてstrにしておく (なぜか仕様がUnion[str, int]である)
    level_order = list(unique_everseen(level_order))  # 重複があったら除去しておく
    omissions = [level for level in level_order if level not in level_order_from_data]  # 抜けがあったら……
    return level_order + omissions  # 後ろにつけておく


def cleanse_bms_table(bms_table: dict) -> dict:
    """
    難易度表データから必須項目のみを抜き出したり後処理をしたりする。

    :param 元データ
    :return: クレンジング後のデータ
    """
    ret = bms_table.copy()

    # 必須項目のみ取り出す (+ときどきある不正な項目にざっと対処)
    ret["data"] = [{"md5": chart["md5"],
                    "level": str(chart["level"])}  # 仕様でstrしか許容されていないが、intを入れている表がある (Overjoy) ので直しておく
                   for chart in bms_table["data"]
                   if len(chart["md5"]) in [32, 160]]  # md5が空文字列のものがある (第2発狂難易度表) ので弾いている。160は段位用

    # 必須項目のみ取り出す。level_orderが省略されているときは仕様に従ってlevel_orderを補完する
    ret["header"] = {"name": bms_table["header"]["name"],
                     "symbol": bms_table["header"]["symbol"],
                     "level_order": get_level_order(ret)}  # ←上で後処理をしたあとのdataを渡している

    return ret
