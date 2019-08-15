from typing import Dict
import luigi

import json

from . import model
from .helper import fetch_bms_table


class BMSTableTarget(luigi.Target):
    def __init__(self, db_url: str, bms_table_path: str):
        self.db_url = db_url
        self.bms_table_path = bms_table_path

    def exists(self):
        return model.stored(self.db_url, self.bms_table_path)

    def get(self) -> Dict[str, str]:
        return model.get(self.db_url, self.bms_table_path)


class FetchBMSTable(luigi.Task):
    db_url = luigi.Parameter()  # type: str
    bms_table_path = luigi.Parameter()  # type: str

    def output(self):
        return BMSTableTarget(db_url=self.db_url, bms_table_path=self.bms_table_path)

    def run(self):
        header_json, data_json = fetch_bms_table(self.bms_table_path)
        model.store(self.db_url, self.bms_table_path, header_json, data_json)


class CrawlBMSTables(luigi.Task):
    db_url = luigi.Parameter()  # type: str
    bms_table_paths = luigi.DictParameter()  # type: Dict[str, str]
    output_path = luigi.Parameter()  # type: str

    def output(self):
        return luigi.LocalTarget(self.output_path)

    def run(self):
        out = []
        for name, path in self.bms_table_paths.items():
            bms_table_task = FetchBMSTable(self.db_url, path)
            yield bms_table_task
            bms_table = bms_table_task.output().get()
            out.append({
                "name": name,
                "path": path,
                "header": json.loads(bms_table["header_json"]),
                "data": json.loads(bms_table["data_json"])
            })

        json.dump(out, open(self.output_path, "w"), indent=2, ensure_ascii=False)
