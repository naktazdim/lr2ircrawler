from  dataclasses import dataclass
from typing import Optional
import re

from lr2ircrawler.fetch import fetch


@dataclass()
class ItemInfo:
    type: str
    lr2_id: int
    title: str


def fetch_ranking_html(hash_value: str, page: int = 4294967295) -> str:
    """
    ランキングページ (html) を取得する。

    ただし、ここではランキングページの上部に書いてある譜面の情報さえ取れればよいので (ランキングそのものを見たいわけではないので)、
    デフォルトではページ数に大きな値を指定しておいて、ランキングそのものは1件も表示されないようにする。以下のような意図。
    [1] 通信量削減 (LR2IRへの負荷対策)
    [2] 飛んでくる html のバリエーションを減らして安定性を高める
        [2-1] ランキングが100件以下かどうかでページ構成が微妙に変わったりする (ページめくり周り)
        [2-2] ランキングを表示するとプレイヤ名に変な文字が入っていたりする可能性がある

    :param hash_value: ハッシュ値
    :param page: ページ数
    :return: html
    """
    if re.match("^[0-9a-f]{32}|[0-9a-f]{160}$", hash_value) is None:
        raise ValueError("hash invalid: {}".format(hash_value))
    url = "http://www.dream-pro.info/~lavalse/LR2IR/search.cgi?mode=ranking&bmsmd5={}&page={}"\
        .format(hash_value, page)
    return fetch(url).decode("cp932")


def extract_item_info(source: str) -> Optional[ItemInfo]:
    if "この曲は登録されていません。<br>" in source.splitlines():
        return None

    bmsid_match = re.search(r"<a href=\"search\.cgi\?mode=editlogList&bmsid=(\d+)\">", source)
    courseid_match = re.search(r"<a href =\"search\.cgi\?mode=downloadcourse&courseid=(\d+)\">", source)
    if bmsid_match:
        item_type, lr2_id = "bms", bmsid_match.group(1)
    elif courseid_match:
        item_type, lr2_id = "course", courseid_match.group(1)
    else:
        raise Exception("parse error: failed to detect lr2 id")

    title_match = re.search(r"<h1>(.*?)</h1>", source)
    if title_match:
        title = title_match.group(1)
    else:
        raise Exception("parse error: failed to detect title")

    return ItemInfo(item_type, int(lr2_id), title)



