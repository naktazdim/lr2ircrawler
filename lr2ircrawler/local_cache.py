import os
import bz2
import sqlite3


def _db_path():
    return os.environ.get("LR2IRCRAWLER_CACHE", "./lr2ircrawler_cache.db")


def _connect():
    return sqlite3.connect(_db_path())


def init():
    conn = _connect()
    conn.cursor().execute("CREATE TABLE IF NOT EXISTS cache (id INTEGER PRIMARY KEY, my_key TEXT UNIQUE, value BLOB)")
    conn.commit()


def save(key: str, value: str):
    conn = _connect()
    conn.cursor().execute("INSERT INTO cache(my_key, value) VALUES (?, ?)", (key, bz2.compress(value)))
    conn.commit()


def load(key: str) -> str:
    value_compressed = _connect().cursor().execute("SELECT value FROM cache WHERE my_key=?", (key,)).fetchone()[0]
    return bz2.decompress(value_compressed)


def exists(key: str) -> bool:
    return _connect().cursor().execute("SELECT id FROM cache WHERE my_key=?", (key,)).fetchone() is not None


def clear():
    os.remove(_db_path())
