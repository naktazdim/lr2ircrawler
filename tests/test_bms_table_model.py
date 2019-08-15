from lr2ircrawler.bms_table import model


def test_bms_table():
    db_url = "sqlite://"
    path = "http://www.example.com/"
    header_json = '"header_json"'
    data_json = '"header_json"'

    assert not model.stored(db_url, path)
    model.store(db_url, path, header_json, data_json)
    assert model.stored(db_url, path)
    assert model.get(db_url, path) == {"path": path, "header_json": header_json, "data_json": data_json}
