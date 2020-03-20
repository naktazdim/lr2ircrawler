from time import sleep
import os
import tempfile
import shutil
from typing import Iterable, Tuple, List

import luigi
import pandas as pd

from . import model
from .helper import fetch_ranking_xml, parse_ranking_xml


def iterate_rankings(db_url: str, bmsmd5s: List[str]) -> Iterable[Tuple[str, pd.DataFrame]]:
    xmls = map(lambda bmsmd5: model.get(db_url, bmsmd5), bmsmd5s)
    rankings = map(parse_ranking_xml, xmls)
    return zip(bmsmd5s, rankings)


class RankingTarget(luigi.Target):
    def __init__(self, db_url: str, bmsmd5: str):
        self.db_url = db_url
        self.bmsmd5 = bmsmd5

    def exists(self):
        return model.stored(self.db_url, self.bmsmd5)

    def get(self) -> str:
        return model.get(self.db_url, self.bmsmd5)


class FetchRanking(luigi.Task):
    db_url = luigi.Parameter()  # type: str
    bmsmd5 = luigi.Parameter()  # type: str
    wait = luigi.FloatParameter(significant=False)  # type: float

    resources = {"lr2ir": 1}  # LR2IRに接続するタスクが同時に一つしか走らないようにする (負荷対策)

    def output(self):
        return RankingTarget(db_url=self.db_url, bmsmd5=self.bmsmd5)

    def run(self):
        sleep(self.wait)  # アクセスのたびに指定した時間だけ待つ (負荷対策)
        xml = fetch_ranking_xml(self.bmsmd5)
        model.store(self.db_url, self.bmsmd5, xml)


class FetchRankings(luigi.WrapperTask):
    db_url = luigi.Parameter()  # type: str
    bmsmd5s = luigi.ListParameter()  # type: List[str]
    wait = luigi.FloatParameter(default=3, significant=False)  # type: float

    def requires(self):
        yield [FetchRanking(db_url=self.db_url, bmsmd5=bmsmd5, wait=self.wait) for bmsmd5 in self.bmsmd5s]


class OutputRecords(luigi.Task):
    db_url = luigi.Parameter()  # type: str
    bmsmd5s = luigi.ListParameter()  # type: List[str]
    output_path = luigi.Parameter()  # type: str

    def output(self):
        return luigi.LocalTarget(self.output_path)

    def run(self):
        # ランキングデータや生成物は比較的大きくなることが予想されるので、一度にメモリ上に展開せず逐次的に読み書きをする方針
        with tempfile.TemporaryDirectory(dir=os.path.dirname(self.output_path)) as temp_dir:  # 一時ディレクトリを作成
            # 一時ディレクトリ下に出力と同名のファイルを作って追記していく
            temp_path = os.path.join(temp_dir, os.path.basename(self.output_path))
            for bmsmd5, ranking in iterate_rankings(self.db_url, self.bmsmd5s):
                (
                    ranking
                    .assign(bmsmd5=bmsmd5)
                    [["bmsmd5", "playerid", "clear", "notes", "combo", "pg", "gr", "minbp"]]
                ).to_csv(temp_path, index=False, mode="a",
                         header=(bmsmd5 == self.bmsmd5s[0]))  # 初回のみヘッダを出力

            # 一通り書き終えたら出力先のディレクトリに移動
            shutil.move(temp_path, os.path.dirname(self.output_path))


class OutputPlayers(luigi.Task):
    db_url = luigi.Parameter()  # type: str
    bmsmd5s = luigi.ListParameter()  # type: List[str]
    output_path = luigi.Parameter()  # type: str

    def output(self):
        return luigi.LocalTarget(self.output_path)

    def run(self):
        # ランキングデータは比較的大きくなることが予想されるので、一度にメモリ上に展開せず逐次的に読み込む方針
        players_dict = {}  # {id: name}
        for _, ranking in iterate_rankings(self.db_url, self.bmsmd5s):
            bms_players_dict = ranking.set_index("playerid").name.to_dict()  # {id: name}
            players_dict.update(bms_players_dict)
        players = pd.DataFrame(zip(players_dict.keys(), players_dict.values()), columns=["playerid", "name"])
        players.astype({"playerid": int}).sort_values(by="playerid").to_csv(self.output_path, index=False)


class CrawlLR2IR(luigi.Task):
    db_url = luigi.Parameter()  # type: str
    bmsmd5s = luigi.ListParameter()  # type: List[str]
    records_output_path = luigi.Parameter()  # type: str
    players_output_path = luigi.Parameter()  # type: str
    wait = luigi.FloatParameter(significant=False, default=3)  # type: float

    def output(self):
        return {
            "records": luigi.LocalTarget(self.records_output_path),
            "players": luigi.LocalTarget(self.players_output_path),
        }

    def run(self):
        yield FetchRankings(db_url=self.db_url, bmsmd5s=self.bmsmd5s, wait=self.wait)
        yield OutputRecords(db_url=self.db_url, output_path=self.records_output_path, bmsmd5s=self.bmsmd5s)
        yield OutputPlayers(db_url=self.db_url, output_path=self.players_output_path, bmsmd5s=self.bmsmd5s)
