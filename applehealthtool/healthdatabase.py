import os
from datetime import datetime
from datetime import timezone
import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Query
from sqlalchemy.orm import aliased
from sqlalchemy.sql import text
from sqlalchemy import func, select
import sqlalchemy.types as types


class TZDateTime(types.TypeDecorator):
    impl = sqlalchemy.DateTime
    cache_ok = True

    def process_bind_param(self, value, dialect):
        # if value is not None:
            # if not value.tzinfo:
            #     raise TypeError("tzinfo is required")
            # value = value.astimezone(timezone.utc).replace(
            #     tzinfo=None
            # )
        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            # value = value.replace(tzinfo=timezone.utc)
            value = value.astimezone()
        return value

Base = declarative_base()

TABLE_NAME = 'health_data'
class HealthData(Base):
    __tablename__ = TABLE_NAME
    id = sqlalchemy.Column(sqlalchemy.INTEGER, primary_key=True, autoincrement=True)
    type = sqlalchemy.Column('type', sqlalchemy.String)
    sourceName = sqlalchemy.Column('sourceName', sqlalchemy.String)
    sourceVersion = sqlalchemy.Column('sourceVersion', sqlalchemy.String)
    device = sqlalchemy.Column('device', sqlalchemy.String)
    unit = sqlalchemy.Column('unit', sqlalchemy.String)
    creationDate = sqlalchemy.Column('creationDate', TZDateTime)
    startDate = sqlalchemy.Column('startDate', TZDateTime)
    endDate = sqlalchemy.Column('endDate', TZDateTime)
    value = sqlalchemy.Column('value', sqlalchemy.String)

class AppleHealthDatabase():
    MAX_COMMIT = 10000 # maximum number of records in single commit
    def __init__(self):
        self.db_path = None
        self.db_engine = None

    def open_database(self, path, echo=False):
        self.db_path = path
        print(f'Opening DB: {self.db_path}')
        uri = f'sqlite:///{self.db_path}'
        print(uri)
        self.db_engine = sqlalchemy.create_engine(uri, echo = echo)
        self.metadata = Base.metadata # sqlalchemy.MetaData(self.db_engine)
        Base.metadata.create_all(self.db_engine)
        self.db_engine.connect()
        print('database open')
        return self.db_engine

    def _open_session(self):
        if not self.db_engine:
            return None
        Session = sessionmaker(bind = self.db_engine)
        return Session()

    def latest_record(self):
        Session = sessionmaker(bind = self.db_engine)
        with Session() as session:
            result = session.query(func.max(HealthData.creationDate)).all()
            return result[0][0]

    def count_rows(self):
        print('count_rows')
        Session = sessionmaker(bind = self.db_engine)
        q = f'SELECT COUNT(*) FROM {TABLE_NAME};'
        with Session() as session:
            n = session.execute(q)
            row = n.fetchone()[0]
            print(f'n: {row}')

            return row

    def get_heart_rate_report(self, startdate=None, enddate=None, sourcename=''):
        if not startdate:
            startdate = datetime.strptime('1970-01-01', "%Y-%m-%d")
        if not enddate:
            enddate = datetime.now()
        if sourcename != '':
            print(f' HR Source: {sourcename}')
            sourcename = f' AND sourceName = "{sourcename}" '
        query = f'''
SELECT DISTINCT startDate, value FROM health_data 
    WHERE type = "HKQuantityTypeIdentifierHeartRate" AND startDate >= "{startdate}" AND endDate <= "{enddate}" {sourcename}
'''
        statement = text(query)
        with self._open_session() as session:
            n = session.execute(statement)
            rows = []
            for r in n:
                cdate = datetime.strptime(r[0], '%Y-%m-%d %H:%M:%S.000000')
                d = {'startDate': cdate, 'heartrate': r[1]}
                rows.append(d)
            return rows

    def get_blood_pressure_report(self, startdate=None, enddate=None, sourcename=''):
        if not startdate:
            startdate = datetime.strptime('1970-01-01', "%Y-%m-%d")
        if not enddate:
            enddate = datetime.now()
        if sourcename != '':
            print(f' BP Source: {sourcename}')
            sourcename = f' AND sourceName = "{sourcename}" '
        query = f'''
SELECT DISTINCT
  s.startDate, s.value 'systolic', d.value 'diastolic'
    FROM
    (
      SELECT startDate, type, value
      FROM health_data
      WHERE
        type = 'HKQuantityTypeIdentifierBloodPressureSystolic' {sourcename}
    ) s
    JOIN
    (
        SELECT startDate, type, value
        FROM health_data
        WHERE
            type = 'HKQuantityTypeIdentifierBloodPressureDiastolic' {sourcename}
    ) d
    ON
        s.startDate = d.startDate AND s.startDate >= '{startdate}' AND s.startDate <= '{enddate}'
    ORDER BY s.startDate
'''
        statement = text(query)
        with self._open_session() as session:
            n = session.execute(statement)
            rows = []
            for r in n:
                cdate = datetime.strptime(r[0], '%Y-%m-%d %H:%M:%S.000000')
                d = {'startDate': cdate, 'systolic': r[1], 'diastolic': r[2]}
                rows.append(d)
            return rows

    def insert_records(self, records, callback=None):
        with self._open_session() as session:
            count = 0
            for record in records:
                session.add(record)
                count += 1
                if count % AppleHealthDatabase.MAX_COMMIT == 0:
                    print(f' - Committing {count} records...')
                    session.commit()
                    if callback:
                        callback(count)
            if count > 0:
                print(f' - Committing {count} records...')
                session.commit()
                if callback:
                    callback(count)
