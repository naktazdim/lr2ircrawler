import os
import json

import luigi

from lr2ircrawler.tasks import MakeBmsTablesJson, MakeCleansedBmsTableJson, MakeItemCsv, MakePlayersCsv, MakeRecordsCsv
from lr2ircrawler import local_cache


class Crawl(luigi.Task):
    targets_json = luigi.Parameter()  # type: str
    output_dir = luigi.Parameter(default=".")  # type: str

    def output(self):
        return {
            "bms_tables_original": luigi.LocalTarget(os.path.join(self.output_dir, "bms_tables_original.json")),
            "bms_tables": luigi.LocalTarget(os.path.join(self.output_dir, "bms_tables.json")),
            "items":      luigi.LocalTarget(os.path.join(self.output_dir, "items.csv")),
            "players":    luigi.LocalTarget(os.path.join(self.output_dir, "players.csv")),
            "records":   luigi.LocalTarget(os.path.join(self.output_dir, "records.csv")),
        }

    def run(self):
        local_cache.init()

        bms_tables_original_task = MakeBmsTablesJson(targets=json.load(open(self.targets_json)),
                                                     output_path=self.output()["bms_tables_original"].path)
        yield bms_tables_original_task
        bms_tables_task = MakeCleansedBmsTableJson(bms_tables_original_json=bms_tables_original_task.output().path,
                                                   output_path=self.output()["bms_tables"].path)
        yield bms_tables_task

        bmsmd5s = {chart["md5"]
                   for bms_table in bms_tables_task.load()
                   for chart in bms_table["data"]}
        yield [MakeItemCsv(bmsmd5s=bmsmd5s, output_path=self.output()["items"].path),
               MakePlayersCsv(bmsmd5s=bmsmd5s, output_path=self.output()["players"].path),
               MakeRecordsCsv(bmsmd5s=bmsmd5s, output_path=self.output()["records"].path)]

        local_cache.clear()


def main():
    luigi.run()


if __name__ == "__main__":
    main()
