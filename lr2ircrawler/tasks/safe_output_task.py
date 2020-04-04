import os
import tempfile
import shutil

import luigi.util


class _SafeOutputTaskBase(luigi.Task):
    output_path = luigi.Parameter()  # type: str

    def output(self):
        return luigi.LocalTarget(self.output_path)

    def save(self, output_path: str):
        # これをオーバーライドしてファイル出力の処理を実装してください
        # self.output_path でなく引数の output_path に出力する処理を書いてください
        raise NotImplementedError

    def run(self):
        # save() が途中で止まっても不完全なファイルが出来ないように、安全に書き出しを行う

        # 出力先と同じファイルシステムに一時ファイルを作ってそこに書き込み処理を行い、書き終わったら出力先に移動する
        # (shutil.move() は移動元と移動先が同じファイルシステムにあるときatomicであることが保証されている)
        # 一時ファイルを NamedTemporaryFile で作らずにいちいち TemporaryDirectory を作っているのは、
        # NamedTemporaryFile だと shutil.move() しても with を抜けたときにファイルが消されてしまうから
        dirname = os.path.dirname(self.output().path)
        with tempfile.TemporaryDirectory(dir=dirname, prefix="lr2ircrawler_tmp_") as temp_dir:
            temp_path = os.path.join(temp_dir, os.path.basename(self.output().path))
            self.save(temp_path)
            shutil.move(temp_path, self.output().path)
