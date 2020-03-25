from typing import Dict, Optional, Callable

import sqlalchemy
import sqlalchemy.orm
from sqlalchemy import Column, Integer, String
from sqlalchemy.schema import UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql.expression import exists

from .helper import ItemInfo

Base = declarative_base()
engine = None  # type: Optional[sqlalchemy.engine.Engine]
Session = None  # type: Optional[Callable[[], sqlalchemy.orm.Session]]
_db_url = None  # type: Optional[str]


class Item(Base):
    __tablename__ = "item"
    __table_args__ = (UniqueConstraint("type", "lr2_id"),)

    id = Column(Integer, primary_key=True)
    bmsmd5 = Column(String(160), nullable=True, unique=True, index=True)
    type = Column(String, nullable=False)
    lr2_id = Column(Integer, nullable=False)
    title = Column(String, nullable=False)


def init(db_url: str):
    global engine, Session, _db_url
    if _db_url != db_url:
        engine = sqlalchemy.create_engine(db_url)
        Session = sqlalchemy.orm.scoped_session(sqlalchemy.orm.sessionmaker(bind=engine))
        Base.metadata.create_all(bind=engine)
        _db_url = db_url


def store(db_url: str, hash_value: str, item_info: ItemInfo):
    init(db_url)
    session = Session()
    session.add(Item(bmsmd5=hash_value, type=item_info.type, lr2_id=item_info.lr2_id, title=item_info.title))
    session.commit()


def stored(db_url: str, hash_value: str) -> bool:
    init(db_url)
    return Session().query(exists().where(Item.bmsmd5 == hash_value)).scalar()


def get(db_url: str, hash_value: str) -> Dict[str, str]:
    init(db_url)
    item = Session().query(Item).filter(Item.bmsmd5 == hash_value).first()
    return {
        "bmsmd5": item.bmsmd5,
        "type": item.type,
        "lr2_id": item.lr2_id,
        "title": item.title
    }
