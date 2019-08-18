from typing import Optional, Callable

import sqlalchemy
import sqlalchemy.orm
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql.expression import exists

Base = declarative_base()
engine = None  # type: Optional[sqlalchemy.engine.Engine]
Session = None  # type: Optional[Callable[[], sqlalchemy.orm.Session]]
_db_url = None  # type: Optional[str]


class Ranking(Base):
    __tablename__ = "ranking"

    id = Column(Integer, primary_key=True)
    bmsmd5 = Column(String(160), index=True, nullable=False, unique=True)  # 160 なのは譜面だけでなくコースに対応するため
    ranking_xml = Column(String, nullable=False)


def init(db_url: str):
    global engine, Session, _db_url
    if _db_url != db_url:
        _db_url = db_url
        engine = sqlalchemy.create_engine(db_url)
        Session = sqlalchemy.orm.scoped_session(sqlalchemy.orm.sessionmaker(bind=engine))
        Base.metadata.create_all(bind=engine)


def store(db_url: str, bmsmd5: str, ranking_xml: str):
    init(db_url)
    session = Session()
    session.add(Ranking(bmsmd5=bmsmd5, ranking_xml=ranking_xml))
    session.commit()


def stored(db_url: str, bmsmd5: str) -> bool:
    init(db_url)
    return Session().query(exists().where(Ranking.bmsmd5 == bmsmd5)).scalar()


def get(db_url: str, bmsmd5: str) -> str:
    init(db_url)
    ranking = Session().query(Ranking).filter(Ranking.bmsmd5 == bmsmd5).first()
    return ranking.ranking_xml
