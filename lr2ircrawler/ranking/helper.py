import re

import pandas as pd

from lr2ircrawler.fetch import fetch


def fetch_ranking_xml(bmsmd5: str) -> str:
    """
    LR2IRのAPIを利用して、指定したbmsmd5に対応するランキングを取得する。

    :param bmsmd5: bmsmd5
    :return: APIの出力
    """
    url = "http://www.dream-pro.info/~lavalse/LR2IR/2/getrankingxml.cgi?id=1&songmd5={}".format(bmsmd5)
    return fetch(url).decode("cp932")


def parse_ranking_xml(source: str) -> pd.DataFrame:
    """
    LR2のランキングAPIの出力を解釈し、DataFrameの形で返す。
    http://www.dream-pro.info/~lavalse/LR2IR/2/getrankingxml.cgi?id=[playerid]&songmd5=[songmd5]
    :param source: ランキングAPIの出力
    :return: DataFrame
    """

    """
    上記APIの出力は以下のような形式をしている。

    #<?xml version="1.0" encoding="shift_jis"?>
    <ranking>
        <score>
            <name>nakt</name>
            <id>35564</id>
            <clear>4</clear>
            <notes>1797</notes>
            <combo>602</combo>
            <pg>1003</pg>
            <gr>680</gr>
            <minbp>39</minbp>
        </score>
        ...
        <score>
            ...
        </score>
    </ranking>
    <lastupdate></lastupdate>

    これはwell-formedなXMLではない (1行目の先頭に # がある、ルート要素が <ranking> と <lastupdate> の2つある)。
    なので、XMLパーサは使わずに単に正規表現でデータを抜き出してしまうほうが楽 (だし速度も速い)。
    """

    columns = ["name", "playerid", "clear", "notes", "combo", "pg", "gr", "minbp"]
    match = re.findall(r"<.*?>(.*?)</.*?>", source)[:-1]  # タグの中身をlistで抽出。[:-1]は<lastupdate>の分を抜いている
    data = [match[i:i + len(columns)] for i in range(0, len(match), len(columns))]  # len(columns) 個ずつ区切る
    return pd.DataFrame(data, columns=columns)
