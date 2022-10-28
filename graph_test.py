#! /usr/bin/env python3
from datetime import datetime

import pygame
from pygame_gui.elements import UIImage
from pygame_gui_extras.app import GuiApp

from applehealthtool.GraphData import DataSeries, DataDateRange
from applehealthtool.TimeDataGraph import UITimeDataGraph
from applehealthtool.healthdatabase import AppleHealthDatabase

test_data = [
    {"date": datetime.strptime("2022-06-01 10:36:23.000000", "%Y-%m-%d %H:%M:%S.000000"), "systolic": 146, "diastolic": 81},
    {"date": datetime.strptime("2022-06-01 11:23:04.000000", "%Y-%m-%d %H:%M:%S.000000"), "systolic": 137, "diastolic": 77},
    {"date": datetime.strptime("2022-06-09 22:39:18.000000", "%Y-%m-%d %H:%M:%S.000000"), "systolic": 146, "diastolic": 85},
    {"date": datetime.strptime("2022-06-16 12:34:13.000000", "%Y-%m-%d %H:%M:%S.000000"), "systolic": 148, "diastolic": 85},
    {"date": datetime.strptime("2022-06-16 12:38:14.000000", "%Y-%m-%d %H:%M:%S.000000"), "systolic": 126, "diastolic": 81},
    {"date": datetime.strptime("2022-06-29 10:53:30.000000", "%Y-%m-%d %H:%M:%S.000000"), "systolic": 123, "diastolic": 73},
    {"date": datetime.strptime("2022-07-04 12:01:39.000000", "%Y-%m-%d %H:%M:%S.000000"), "systolic": 152, "diastolic": 77},
    {"date": datetime.strptime("2022-07-04 12:03:08.000000", "%Y-%m-%d %H:%M:%S.000000"), "systolic": 130, "diastolic": 73},
    {"date": datetime.strptime("2022-07-04 12:06:15.000000", "%Y-%m-%d %H:%M:%S.000000"), "systolic": 134, "diastolic": 75},
    {"date": datetime.strptime("2022-07-16 08:31:36.000000", "%Y-%m-%d %H:%M:%S.000000"), "systolic": 135, "diastolic": 85},
    {"date": datetime.strptime("2022-07-16 08:34:42.000000", "%Y-%m-%d %H:%M:%S.000000"), "systolic": 130, "diastolic": 81},
    {"date": datetime.strptime("2022-07-26 16:25:48.000000", "%Y-%m-%d %H:%M:%S.000000"), "systolic": 121, "diastolic": 76},
    {"date": datetime.strptime("2022-07-26 16:28:50.000000", "%Y-%m-%d %H:%M:%S.000000"), "systolic": 128, "diastolic": 75},
    {"date": datetime.strptime("2022-07-28 18:30:52.000000", "%Y-%m-%d %H:%M:%S.000000"), "systolic": 139, "diastolic": 77},
    {"date": datetime.strptime("2022-07-28 18:33:06.000000", "%Y-%m-%d %H:%M:%S.000000"), "systolic": 121, "diastolic": 76},
    {"date": datetime.strptime("2022-07-31 10:21:52.000000", "%Y-%m-%d %H:%M:%S.000000"), "systolic": 124, "diastolic": 73},
    {"date": datetime.strptime("2022-07-31 10:23:41.000000", "%Y-%m-%d %H:%M:%S.000000"), "systolic": 132, "diastolic": 71},
    {"date": datetime.strptime("2022-07-31 10:26:29.000000", "%Y-%m-%d %H:%M:%S.000000"), "systolic": 124, "diastolic": 72},
    {"date": datetime.strptime("2022-08-04 12:13:24.000000", "%Y-%m-%d %H:%M:%S.000000"), "systolic": 134, "diastolic": 85},
    {"date": datetime.strptime("2022-08-04 12:15:11.000000", "%Y-%m-%d %H:%M:%S.000000"), "systolic": 127, "diastolic": 81},
    {"date": datetime.strptime("2022-08-04 12:17:26.000000", "%Y-%m-%d %H:%M:%S.000000"), "systolic": 134, "diastolic": 79},
    {"date": datetime.strptime("2022-08-06 11:36:45.000000", "%Y-%m-%d %H:%M:%S.000000"), "systolic": 122, "diastolic": 70},
    {"date": datetime.strptime("2022-08-07 09:06:30.000000", "%Y-%m-%d %H:%M:%S.000000"), "systolic": 121, "diastolic": 83},
    {"date": datetime.strptime("2022-08-09 10:39:37.000000", "%Y-%m-%d %H:%M:%S.000000"), "systolic": 150, "diastolic": 80},
    {"date": datetime.strptime("2022-08-09 10:41:21.000000", "%Y-%m-%d %H:%M:%S.000000"), "systolic": 140, "diastolic": 78},
    {"date": datetime.strptime("2022-08-09 10:42:50.000000", "%Y-%m-%d %H:%M:%S.000000"), "systolic": 124, "diastolic": 80},
    {"date": datetime.strptime("2022-08-09 10:44:44.000000", "%Y-%m-%d %H:%M:%S.000000"), "systolic": 125, "diastolic": 77},
    {"date": datetime.strptime("2022-08-13 12:26:19.000000", "%Y-%m-%d %H:%M:%S.000000"), "systolic": 134, "diastolic": 74},
    {"date": datetime.strptime("2022-08-13 12:27:18.000000", "%Y-%m-%d %H:%M:%S.000000"), "systolic": 120, "diastolic": 74},
    {"date": datetime.strptime("2022-08-13 12:28:29.000000", "%Y-%m-%d %H:%M:%S.000000"), "systolic": 125, "diastolic": 76},
    {"date": datetime.strptime("2022-08-15 12:45:50.000000", "%Y-%m-%d %H:%M:%S.000000"), "systolic": 127, "diastolic": 75},
    {"date": datetime.strptime("2022-08-15 12:48:05.000000", "%Y-%m-%d %H:%M:%S.000000"), "systolic": 126, "diastolic": 71},
    {"date": datetime.strptime("2022-08-15 12:49:10.000000", "%Y-%m-%d %H:%M:%S.000000"), "systolic": 120, "diastolic": 75},
]


class GraphTestApp(GuiApp):
    def __init__(self, size=(1280, 960)):
        super().__init__(size, title='Graph Test Tool')

        self.graph = UITimeDataGraph(
            pygame.Rect((0, 0), size),
            manager=self.ui_manager,
            title='Graph Test',
            anchors={
                'top': 'top', 'left': 'left',
                'bottom': 'bottom', 'right': 'right'
            }
        )

    def add_data(self, data_set:DataSeries):
        self.graph.add_data(data_set)

    def add_sleep_data(self, data:DataDateRange):
        if data.data_count > 0:
            self.graph.add_sleep_data(data)

    def set_date_range(self, startdate, enddate):
        d = datetime.strptime(startdate, "%Y-%m-%d")
        date0 = datetime.timestamp(d)
        d = datetime.strptime(enddate, "%Y-%m-%d")
        date1 = datetime.timestamp(d)
        self.graph._xscaler.update_data_limits(date0, date1)
        print(f'date range: {date0} to {date1}')

    def setup(self):
        # self.graph.add_data(data_series)
        self.graph.redraw()

DB_PATH = './health.db'

if __name__ == '__main__':
    database = AppleHealthDatabase()
    db_engine = database.open_database(DB_PATH, echo=True)
    app = GraphTestApp()

    startdate = '2022-07-03'
    startdate = '2022-08-08'
    enddate = '2022-08-10'

    # SLEEP START / END : 2021-08-02 22:46:01.000000|2022-08-15 08:01:00.000000
    #startdate = '2022-08-09 04:32:00'
    #enddate = '2022-08-10 14:42:00'
    sourcename = ''

    # sourcename = 'FitCloudPro'
    app.set_date_range(startdate, enddate)

    bp_data = database.get_blood_pressure_report(startdate=startdate, enddate=enddate, sourcename=sourcename)
    print(f'** BP Count: {len(bp_data)}')
    if len(bp_data) > 0:
        print(f'** BP Start: {bp_data[0]["startDate"]}')
        print(f'** BP   End: {bp_data[-1]["startDate"]}')
        data_series = DataSeries('blood pressure', bp_data,
                             x_data_col='startDate',
                             y_data_cols=['systolic', 'diastolic'],
                             label='blood pressure',
                             timeseries=True,
                             color=pygame.Color(200, 0, 0, 255),
                             line_width=3
                             )
        print(f'    BP min/max: {data_series.x_minmax}, {data_series.y_minmax}')
        app.add_data(data_series)

    hr_data = database.get_heart_rate_report(startdate=startdate, enddate=enddate, sourcename=sourcename)
    print(f'** HR Count: {len(hr_data)}')
    if len(hr_data) > 0:
        print(f'** HR Start: {hr_data[0]["startDate"]}')
        print(f'** HR   End: {hr_data[-1]["startDate"]}')
        hr_series = DataSeries('heart rate', hr_data,
                           x_data_col='startDate',
                           y_data_cols=['heartrate'],
                           label='heart rate',
                           timeseries=True,
                           color=pygame.Color(0, 200, 0, 255),
                           line_width=3)

        app.add_data(hr_series)

    sleep_data = database.get_sleep_report(startdate=startdate, enddate=enddate, sourcename=sourcename)
    print(f'** SLEEP Count: {len(sleep_data)}')
    if len(sleep_data) > 0:
        print(f'** SLEEP Start: {sleep_data[0]["startDate"]} to {sleep_data[0]["endDate"]}: {sleep_data[0]["value"]}')
        print(f'** SLEEP End: {sleep_data[-1]["startDate"]} to {sleep_data[-1]["endDate"]}: {sleep_data[-1]["value"]}')
    sleep_series = DataDateRange('sleep', sleep_data, 'startDate', 'endDate', 'value', {})
    app.add_sleep_data(sleep_series)


    app.setup()
    app.graph.save_to_image('GRAPHTEST.png')
    app.run()
