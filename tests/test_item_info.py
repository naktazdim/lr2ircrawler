import pytest

from lr2ircrawler.item_info.helper import extract_item_info, ItemInfo

from .util import resource


@pytest.mark.parametrize('source,info', [
    (resource("bms.html"),
     ItemInfo("bms", 208408, "Espresso Shots [convert]")),
    (resource("course.html"),
     ItemInfo("course", 11099, "GENOSIDE 2018 段位認定 Overjoy")),
])
def test_extract_item_info(source: str, info: ItemInfo):
    assert extract_item_info(source) == info


def test_extract_item_info_unregistered():
    source = resource("unregistered.html")
    assert extract_item_info(source) is None
