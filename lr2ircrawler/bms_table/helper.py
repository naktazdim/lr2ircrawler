from urllib.parse import urljoin
from io import BytesIO
from typing import Tuple
import json

import lxml.html

from lr2ircrawler.fetch import fetch


def fetch_bms_table(path: str) -> Tuple[str, str]:
    """
    指定したURLから難易度表を取得し、「ヘッダ部」「データ部」のJSON stringを返す。
    http://bmsnormal2.syuriken.jp/bms_dtmanager.html

    :param path: 難易度表のパス
    :return: (ヘッダ部), (データ部)
    """
    html = fetch(path)
    tree = lxml.html.parse(BytesIO(html))

    header_json_path = tree.xpath("/html/head/meta[@name='bmstable']/@content")[0]
    header_json_path = urljoin(path, header_json_path)

    header_json = fetch(header_json_path).decode("utf-8-sig")  # 仕様で UTF-8 と決まっている
    # "utf-8" だと BOM あり UTF-8 が読めない。 utf-8-sig は BOM ありもなしもどちらも読める

    data_json_path = json.loads(header_json)["data_url"]
    data_json_path = urljoin(header_json_path, data_json_path)
    data_json = fetch(data_json_path).decode("utf-8-sig")  # 仕様で UTF-8 と決まっている

    return header_json, data_json
