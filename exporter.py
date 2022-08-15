import argparse
import datetime
import os.path

import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import sys
import xml.etree.ElementTree as ET

print(f'SQLAlchemy Version: {sqlalchemy.__version__}')
Base = declarative_base()

class HealthData(Base):
    ### Schema:
    # type           : HKQuantityTypeIdentifierHeight
    # sourceName     : Health
    # sourceVersion  : _string_
    # device         : _string_
    # unit           : _string_
    # creationDate   : 2015-05-03 16:58:00 -0700
    # startDate      : 2015-05-03 16:58:00 -0700
    # endDate        : 2015-05-03 16:58:00 -0700
    # value          : 5.83333
    __tablename__ = 'health_data'
    id = sqlalchemy.Column(sqlalchemy.INTEGER, primary_key=True, autoincrement=True)
    type = sqlalchemy.Column('type', sqlalchemy.String)
    sourceName = sqlalchemy.Column('sourceName', sqlalchemy.String)
    sourceVersion = sqlalchemy.Column('sourceVersion', sqlalchemy.String)
    device = sqlalchemy.Column('device', sqlalchemy.String)
    unit = sqlalchemy.Column('unit', sqlalchemy.String)
    creationDate = sqlalchemy.Column('creationDate', sqlalchemy.DateTime)
    startDate = sqlalchemy.Column('startDate', sqlalchemy.DateTime)
    endDate = sqlalchemy.Column('endDate', sqlalchemy.DateTime)
    value = sqlalchemy.Column('value', sqlalchemy.String)


def make_datetime(datetime_string):
    format = '%Y-%m-%d %H:%M:%S %z'
    return datetime.datetime.strptime(datetime_string, format)


def dump_elem_attr(attrib):
    for k in attrib:
        print(f'{k:15}: {attrib[k]}')


def import_data(config, db):
    xmlfile = config.input
    print(f'importing {xmlfile}')

    startdate = None
    dateformat = "%Y-%m-%d"
    if config.start:
        startdate = datetime.datetime.strptime(config.start, dateformat)

    tree = ET.parse(xmlfile)
    root = tree.getroot()

    records = {}

    tags = {
        'HKQuantityTypeIdentifierBloodPressureDiastolic': 'diastolic',
        'HKQuantityTypeIdentifierBloodPressureSystolic': 'systolic',
        'HKQuantityTypeIdentifierHeartRate': 'heart-rate',
        'HKQuantityTypeIdentifierBodyMass': 'weight',
        'HKQuantityTypeIdentifierHeight': 'height',
        'HKQuantityTypeIdentifierActiveEnergyBurned': 'calories',
        'HKQuantityTypeIdentifierFlightsClimbed': 'stairs',
        'HKQuantityTypeIdentifierStepCount': 'steps',
        'HKQuantityTypeIdentifierDistanceWalkingRunning': 'distance'
    }
    Session = sessionmaker(bind = db)
    session = Session()
    rcount = 0
    total_count = 0
    COMMIT_MAX = 100000
    for elem in root:
        if elem.tag == 'Record':
            record = HealthData(
                type = elem.attrib['type'],
                sourceName = elem.attrib['sourceName'],
                sourceVersion = elem.attrib['sourceVersion'] if 'sourceVersion' in elem.attrib else '',
                device = str(elem.attrib['device']) if 'device' in elem.attrib else '',
                unit = elem.attrib['unit'] if 'unit' in elem.attrib else '',
                creationDate = make_datetime(elem.attrib['creationDate']),
                startDate = make_datetime(elem.attrib['startDate']),
                endDate = make_datetime(elem.attrib['endDate']),
                value = elem.attrib['value']
            )
            session.add(record)
            rcount += 1
            total_count += 1
            if rcount >= COMMIT_MAX:
                print(f'commit {COMMIT_MAX} records...')
                session.commit()
                rcount = 0

    if rcount > 0:
        session.commit()
    print(f'Total of {total_count} records')

def parse_command_line():
    parser = argparse.ArgumentParser()
    parser.add_argument('--database', '-d', help='Path to sqlite database', type=str, required=True)
    parser.add_argument('--input', '-i', help='Path to Apple Health XML file', type=str)
    parser.add_argument('--start', '-s', help='Date to start report', default=None, type=str)
    return parser.parse_args()

def open_database(config):
    print(f'Opening DB: {config.database}')
    if os.path.exists(config.database):
        os.remove(config.database)
    uri = f'sqlite:///{config.database}'
    print(uri)
    db = sqlalchemy.create_engine(uri, echo = False)
    TABLE_NAME = 'health_data'
    ### Schema:
    # type           : HKQuantityTypeIdentifierHeight
    # sourceName     : Health
    # unit           : ft
    # creationDate   : 2015-05-03 16:58:00 -0700
    # startDate      : 2015-05-03 16:58:00 -0700
    # endDate        : 2015-05-03 16:58:00 -0700
    # value          : 5.83333
    metadata = sqlalchemy.MetaData(db)
    Base.metadata.create_all(db)
    db.connect()
    return db

if __name__ == '__main__':
    config = parse_command_line()
    db = open_database(config)
    import_data(config, db)