import os
import json
import bz2

import luigi
from lr2ircrawler.bms_table import CrawlBMSTables
from lr2ircrawler.ranking import CrawlLR2IR
from lr2ircrawler.fetch import fetch


class CrawlLR2IRByBMSTables(luigi.Task):
    target = luigi.Parameter()  # type: str
    db_url = luigi.Parameter(default="sqlite:///lr2ircrawler.db")  # type: str
    output_dir = luigi.Parameter(default=".")  # type: str
    wait = luigi.FloatParameter(significant=False, default=3)  # type: float

    def output(self):
        return {
            "bms_tables": luigi.LocalTarget(os.path.join(self.output_dir, "bms_tables.json.bz2")),
            "records": luigi.LocalTarget(os.path.join(self.output_dir, "records.csv.bz2")),
            "players": luigi.LocalTarget(os.path.join(self.output_dir, "players.csv.bz2"))
        }

    def run(self):
        bms_table_paths = json.loads(fetch(self.target))
        bms_tables_task = CrawlBMSTables(
            db_url=self.db_url,
            bms_table_paths=bms_table_paths,
            output_path=self.output()["bms_tables"].path
        )
        yield bms_tables_task

        bms_tables = json.load(bz2.open(bms_tables_task.output().path, "rt"))
        bmsmd5s = [chart["md5"] for bms_table in bms_tables for chart in bms_table["data"]
                   if len(chart["md5"]) in [32, 160]]  # 第2発狂難易度表にmd5フィールドが空文字列の譜面があるので対策

        yield CrawlLR2IR(
            db_url=self.db_url,
            bmsmd5s=bmsmd5s,
            records_output_path=self.output()["records"].path,
            players_output_path=self.output()["players"].path,
            wait=self.wait
        )


if __name__ == "__main__":
    luigi.run()
