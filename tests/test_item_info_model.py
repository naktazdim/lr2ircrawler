from dataclasses import asdict

from lr2ircrawler.item_info import model
from lr2ircrawler.item_info.helper import ItemInfo


def test_item_info():
    db_url = "sqlite://"
    bmsmd5 = "758dcee38a5931b3fb0d0a61feddb324"
    item_info = ItemInfo("bms", 208408, "Espresso Shots [convert]")

    assert not model.stored(db_url, bmsmd5)
    model.store(db_url, bmsmd5, item_info)
    assert model.stored(db_url, bmsmd5)
    ret = model.get(db_url, bmsmd5)
    assert bmsmd5 == ret.pop("bmsmd5")
    assert ret == asdict(item_info)

