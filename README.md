[LunaticRave2 Internet Ranking (LR2IR)](http://www.dream-pro.info/~lavalse/LR2IR/search.cgi) から、指定した難易度表のランキングデータを収集する

# Usage
[Luigi](https://luigi.readthedocs.io/en/stable/) のTaskとして実装されている。
例えば以下のように実行する。
```commandline
$ export PYTHONPATH=/path/to/lr2ircrawler/:$PYTHONPATH
$ luigi --local-scheduler \
	--module lr2ircrawler.main CrawlLR2IRByBMSTables \
	--target TARGET \
	--output-dir OUTPUT_DIR \
	--db-url DB_URL \
	--wait WAIT
```

## 入力
TARGET に収集対象を以下のように記述した JSON ファイルのパスを指定する。

- キー (以下の例では "insane", "overjoy") は難易度表を識別するための好きな名前
- URLは[次期難易度表フォーマット](http://bmsnormal2.syuriken.jp/bms_dtmanager.html)のものであること
 
 
```json
{
	"insane": "http://www.ribbit.xyz/bms/tables/insane.html",
	"overjoy": "http://lr2.sakura.ne.jp/overjoy.php"
}
```

### オプション引数
| オプション | デフォルト | 説明 |
|-:|:-|:-|
|`--output-dir`|. <br> (カレントディレクトリ) | データ出力先 |
|`--db-url`| sqlite:///lr2ircrawler.db <br> (SQLite, カレントディレクトリ下) |処理中のデータを格納するデータベース<br>[参考リンク](http://omake.accense.com/static/doc-ja/sqlalchemy/dbengine.html#create-engine-url)|
|`--wait`| 3.0 | LR2IRにアクセスする間隔 (秒)|

## 出力
OUTPUT_DIR (デフォルトはカレントディレクトリ) 以下に

- bms_tables.json
- records.csv.bz2
- players.csv.bz2 

の3ファイルを出力する。

### bms_tables.json
以下のようなJSONファイル

- name, path は入力で指定したもの
- header, data は[次期難易度表フォーマット](http://bmsnormal2.syuriken.jp/bms_dtmanager.html)の「ヘッダ部」「データ部」
```json
[
  {
    "name": "insane",
    "path": "http://www.ribbit.xyz/bms/tables/insane.html",
    "header": {...},
    "data": {...}
  },
  ...
]
```
### records.csv(.bz2)
LR2IRのAPIから得られる値ほぼそのまま。

| カラム名 | 説明 |
|-----------:|:------------|
|bmsmd5|譜面の bmsmd5|
|playerid|プレイヤの LR2 ID|
|clear|クリア状況<br>(1: Failed, 2: Easy, 3: Normal, 4: Hard, 5: Full Combo)|
|combo|最大コンボ数|
|pg|PGREAT数|
|gr|GREAT数|
|minbp|最小BP数|

### players.csv(.bz2)
| カラム名 | 説明 |
|-----------:|:------------|
|playerid|プレイヤの LR2 ID|
|name|プレイヤ名|


## Requirements
* Python 3
* sqlalchemy, pandas, luigi, lxml, requests, chardet