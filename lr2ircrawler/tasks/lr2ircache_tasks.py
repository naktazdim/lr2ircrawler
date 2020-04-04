from typing import List, Iterator, Tuple
import json
import os

import luigi
import requests

from lr2ircrawler import local_cache


class _CallLr2irCacheApi(luigi.Task):
    endpoint = luigi.Parameter()  # type: str
    _session = requests.Session()

    def complete(self):
        return local_cache.exists(self.endpoint)

    def load(self):
        return json.loads(local_cache.load(self.endpoint))

    def run(self):
        r = self._session.get(os.environ["LR2IRCACHE_URL"] + self.endpoint)
        r.raise_for_status()
        local_cache.save(self.endpoint, r.content)


class _DownloadRankings(luigi.WrapperTask):
    bmsmd5s = luigi.ListParameter()  # type: List[str]

    def requires(self):
        return {bmsmd5: _CallLr2irCacheApi("/rankings/" + bmsmd5)
                for bmsmd5 in self.bmsmd5s}

    def rankings(self) -> Iterator[Tuple[str, List[dict]]]:
        for bmsmd5, task in self.requires().items():
            yield bmsmd5, task.load()

