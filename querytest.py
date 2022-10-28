from applehealthtool.healthdatabase import AppleHealthDatabase

DB_PATH = './health.db'
if __name__ == '__main__':
    database = AppleHealthDatabase()
    db_engine = database.open_database(DB_PATH, echo=True)

    nrows = database.count_rows()
    print(f'Database has {nrows} rows')

    # bp_data = database.XXX()
