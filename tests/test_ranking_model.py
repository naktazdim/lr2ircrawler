from lr2ircrawler.ranking import model


def test_ranking():
    db_url = "sqlite://"
    bmsmd5 = "00000000000000000000000000000000"
    ranking_xml = "<test></test>"

    assert not model.stored(db_url, bmsmd5)
    model.store(db_url, bmsmd5, ranking_xml)
    assert model.stored(db_url, bmsmd5)
    assert model.get(db_url, bmsmd5) == ranking_xml
