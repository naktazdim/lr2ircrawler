from typing import Dict, List
from time import sleep

import luigi

from . import model
from .helper import fetch_ranking_html, extract_item_info


class ItemInfoTarget(luigi.Target):
    def __init__(self, db_url: str, bmsmd5: str):
        self.db_url = db_url
        self.bmsmd5 = bmsmd5

    def exists(self):
        return model.stored(self.db_url, self.bmsmd5)

    def get(self) -> Dict[str, str]:
        return model.get(self.db_url, self.bmsmd5)


class FetchItemInfo(luigi.Task):
    db_url = luigi.Parameter()  # type: str
    bmsmd5 = luigi.Parameter()  # type: str
    wait = luigi.FloatParameter(significant=False)  # type: float

    resources = {"lr2ir": 1}  # LR2IRに接続するタスクが同時に一つしか走らないようにする (負荷対策)

    def output(self):
        return ItemInfoTarget(db_url=self.db_url, bmsmd5=self.bmsmd5)

    def run(self):
        sleep(self.wait)  # アクセスのたびに指定した時間だけ待つ (負荷対策)
        source = fetch_ranking_html(self.bmsmd5)
        item_info = extract_item_info(source)
        model.store(self.db_url, self.bmsmd5, item_info)


class CrawlItemInfo(luigi.Task):
    db_url = luigi.Parameter()  # type: str
    bmsmd5s = luigi.ListParameter()  # type: List[str]
    wait = luigi.FloatParameter(default=3, significant=False)  # type: float

    def requires(self):
        yield [FetchItemInfo(db_url=self.db_url, bmsmd5=bmsmd5, wait=self.wait) for bmsmd5 in self.bmsmd5s]
