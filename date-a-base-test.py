import datetime
import locale
import sys
import pytz

import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import func
import sqlalchemy.types as types


class TZDateTime(types.TypeDecorator):
    impl = sqlalchemy.DateTime
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is not None:
            if not value.tzinfo:
                raise TypeError("tzinfo is required")
            value = value.astimezone(datetime.timezone.utc).replace(
                tzinfo=None
            )
            print(f'VALUE: {value}')
        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            value = value.replace(tzinfo=datetime.timezone.utc)
            print(f'RESULT VALUE: {value}')
            value = value.astimezone()
            print(f'RESULT VALUE: {value}')
        return value

Base = declarative_base()

TABLE_NAME = 'datetest'
class DateData(Base):
    __tablename__ = TABLE_NAME
    id = sqlalchemy.Column(sqlalchemy.INTEGER, primary_key=True, autoincrement=True)
    creationDate = sqlalchemy.Column('creationDate', TZDateTime)

class datetestdb():
    def __init__(self):
        self.db_path = None
        self.db_engine = None

    def open_database(self, path):
        self.db_path = path
        print(f'Opening DB: {self.db_path}')
        uri = f'sqlite:///{self.db_path}'
        print(uri)
        self.db_engine = sqlalchemy.create_engine(uri, echo = False)
        self.metadata = Base.metadata # sqlalchemy.MetaData(self.db_engine)
        Base.metadata.create_all(self.db_engine)
        self.db_engine.connect()
        print('database open')
        return self.db_engine

    def open_session(self):
        if not self.db_engine:
            return None
        Session = sessionmaker(bind = self.db_engine)
        return Session()

    def add_record(self, date_in):
        with self.open_session() as session:
            session.add(DateData(creationDate=date_in))
            session.commit()

    def get_latest(self):
        with self.open_session() as session:
            result = session.query(func.max(DateData.creationDate)).all()
            return result[0][0]

if __name__ == '__main__':
    dateabase = datetestdb()
    dateabase.open_database('datetest.db')

    date_in = datetime.datetime.now().astimezone()
    print(f'Date In : {date_in}')

    dateabase.add_record(date_in)
    date_out = dateabase.get_latest()
    print(f'Date Out: {date_out.astimezone()}')
