[LunaticRave2 Internet Ranking (LR2IR)](http://www.dream-pro.info/~lavalse/LR2IR/search.cgi) から、指定した難易度表のランキングデータを収集する

# Requirements

* Python 3
* pandas, luigi, requests

# Usage

[Luigi](https://luigi.readthedocs.io/en/stable/) のTaskとして実装されている。
例えば以下のように実行する。

```sh
$ PYTHONPATH=/path/to/lr2ircrawler/:$PYTHONPATH luigi \
		--local-scheduler \
		--module lr2ircrawler Crawl \
		--targets-json TARGET \
		--output-dir OUTPUT_DIR
```

## 入力
TARGET に収集対象を以下のように記述した JSON ファイルのパスを指定する。

- キー (以下の例では "insane", "overjoy") は難易度表を識別するための好きな名前
- URLは[次期難易度表フォーマット](http://bmsnormal2.syuriken.jp/bms_dtmanager.html)のものであること。次期難易度表フォーマットに沿った「コースの表」を作って指定することもできる。


```json
{
	"insane": "http://www.ribbit.xyz/bms/tables/insane.html",
	"overjoy": "http://lr2.sakura.ne.jp/overjoy.php",
  "dan": "https://lr2ircrawler.s3-ap-northeast-1.amazonaws.com/targets/sp_dan_2018/index.html"
}
```

## 出力

OUTPUT_DIR (デフォルトはカレントディレクトリ) 以下に

- bms_tables_original.json
- bms_tables.json
- items.csv
- players.csv
- rankings.csv

の5ファイルを出力する。

### bms_tables_original.json
以下のようなJSONファイル

- id, url は入力で指定したキーとURL
- header, data は[次期難易度表フォーマット](http://bmsnormal2.syuriken.jp/bms_dtmanager.html)の「ヘッダ部」「データ部」
```json
[
  {
    "id": "insane",
    "url": "http://www.ribbit.xyz/bms/tables/insane.html",
    "header": {...},
    "data": {...}
  },
  ...
]
```
### bms_tables.json

bms_tables_original.jsonに以下の処理を加えたもの (必須項目のみ抽出 + α)。

* ヘッダ部はname, symbol, level_orderのみ。
  * 元データでlevel_orderが省略されている場合にもlevel_orderを補完 (仕様に従い、「データ部のレベル検出順」)
  * 仕様ではlevel_orderにはstrとintが許容されているが、データ部のlevelに合わせて強制的にstrに変換
* データ部はmd5, levelのみ
  * md5: 第2発狂難易度表にmd5が空欄のものがあったりするので、md5の長さがおかしい項目は除外
  * level: 仕様でstrと定まっているが、Overjoyのように誤ってintを入れている表があるので、強制的にstrに変換

### records.csv
LR2IRのAPIから得られる値そのまま。

- notes は譜面のみに依存する値なのでここに格納されているべきではない (正規形でない) が、APIの出力をそのまま出力している。基本的に同じ譜面であれば全てのプレイヤのレコードに対して同じ値が入っているはずだが、LR2IR側の不具合でまれに値がずれていることがある。

| カラム名 | 説明 |
|-----------:|:------------|
|bmsmd5|譜面の bmsmd5|
|playerid|プレイヤの LR2 ID|
|clear|クリア状況<br>(1: Failed, 2: Easy, 3: Normal, 4: Hard, 5: Full Combo)|
|notes|譜面のノート数|
|combo|最大コンボ数|
|pg|PGREAT数|
|gr|GREAT数|
|minbp|最小BP数|

### players.csv
| カラム名 | 説明 |
|-----------:|:------------|
|playerid|プレイヤの LR2 ID|
|name|プレイヤ名|

### items.csv

| カラム名 | 説明                           |
| -------: | :----------------------------- |
|   bmsmd5 | 譜面の bmsmd5                  |
|     type | "bms" ないし "course"          |
|   lr2_id | LR2IR の bmsid ないし courseid |
|    title | 譜面の名前                     |

## キャッシュについて

環境変数 `LR2IRCRAWLER_CACHE` で指定したパス (指定しなかった場合は `./lr2ircrawler_cache.db`) にキャッシュが保存される。

- すべてのファイルの生成が完了したら、キャッシュは自動で削除される。
- 途中で失敗した場合はキャッシュが残り、単に再実行するだけで途中から再開することができる。不要な場合や最初から実行し直したい場合はキャッシュを手動で削除すること。