from typing import List, Dict
import json

import luigi.util
import pandas as pd

from .lr2ircache_tasks import _CallLr2irCacheApi, _DownloadRankings
from .safe_output_task import _SafeOutputTaskBase
from .cleanse_bms_table import cleanse_bms_table


class MakeBmsTablesJson(_SafeOutputTaskBase):
    targets = luigi.DictParameter()  # type: Dict[str, str]

    def requires(self):
        return {table_id: _CallLr2irCacheApi("/bms_tables?url=" + url)
                for table_id, url in self.targets.items()}

    def save(self, output_path: str):
        bms_tables = [{"id": table_id,
                       "url": self.targets[table_id],
                       **task.load()}
                      for table_id, task in self.requires().items()]
        json.dump(bms_tables, open(output_path, "w"), indent=2, ensure_ascii=False)


class MakeCleansedBmsTableJson(_SafeOutputTaskBase):
    bms_tables_original_json = luigi.Parameter()  # type: str

    def save(self, output_path: str):
        json.dump(
            list(map(cleanse_bms_table, json.load(open(self.bms_tables_original_json)))),
            open(output_path, "w"), indent=2, ensure_ascii=False
        )

    def load(self) -> dict:
        return json.load(open(self.output().path))


class MakeItemCsv(_SafeOutputTaskBase):
    bmsmd5s = luigi.ListParameter()  # type: List[str]

    def requires(self):
        return [_CallLr2irCacheApi("/items/" + bmsmd5)
                for bmsmd5 in self.bmsmd5s]

    def save(self, output_path: str):
        (pd.DataFrame([task.load() for task in self.requires()])
         [["bmsmd5", "type", "lr2_id", "title"]]
         .to_csv(output_path, index=False))


@luigi.util.requires(_DownloadRankings)
class MakeRecordsCsv(_SafeOutputTaskBase):
    def save(self, output_path: str):
        # 生成物は比較的大きくなることが予想されるので、一度にメモリ上に展開せず逐次的に読み書きをする方針
        for i, (bmsmd5, ranking) in enumerate(self.requires().rankings()):
            (pd.DataFrame(ranking)
             .assign(bmsmd5=bmsmd5)
             .rename(columns={"id": "playerid"})
             [["bmsmd5", "playerid", "clear", "notes", "combo", "pg", "gr", "minbp"]]
             .to_csv(output_path, index=False, mode="a", header=(i == 0)))  # 追記、初回のみヘッダを出力


@luigi.util.requires(_DownloadRankings)
class MakePlayersCsv(_SafeOutputTaskBase):
    def save(self, output_path: str):
        players = {}
        for _, ranking in self.requires().rankings():
            chart_players = {record["id"]: record["name"] for record in ranking}
            players.update(chart_players)
        players_df = pd.DataFrame(
            zip(players.keys(), players.values()),
            columns=["playerid", "name"])
        players_df.to_csv(output_path, index=False)

