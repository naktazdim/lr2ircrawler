from typing import Dict, Optional, Callable

import sqlalchemy
import sqlalchemy.orm
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql.expression import exists

Base = declarative_base()
engine = None  # type: Optional[sqlalchemy.engine.Engine]
Session = None  # type: Optional[Callable[[], sqlalchemy.orm.Session]]
_db_url = None  # type: Optional[str]


class BMSTable(Base):
    __tablename__ = "bms_table"

    id = Column(Integer, primary_key=True)
    path = Column(String, index=True, nullable=False, unique=True)
    header_json = Column(String, nullable=False)
    data_json = Column(String, nullable=False)


def init(db_url: str):
    global engine, Session, _db_url
    if _db_url != db_url:
        engine = sqlalchemy.create_engine(db_url)
        Session = sqlalchemy.orm.scoped_session(sqlalchemy.orm.sessionmaker(bind=engine))
        Base.metadata.create_all(bind=engine)
        _db_url = db_url


def store(db_url: str, bms_table_path: str, header_json: str, data_json: str):
    init(db_url)
    session = Session()
    session.add(BMSTable(path=bms_table_path, header_json=header_json, data_json=data_json))
    session.commit()


def stored(db_url: str, bms_table_path: str) -> bool:
    init(db_url)
    return Session().query(exists().where(BMSTable.path == bms_table_path)).scalar()


def get(db_url: str, bms_table_path: str) -> Dict[str, str]:
    init(db_url)
    bms_table = Session().query(BMSTable).filter(BMSTable.path == bms_table_path).first()
    return {
            "path": bms_table.path,
            "header_json": bms_table.header_json,
            "data_json": bms_table.data_json
        }
