#! /usr/bin/env python3
from datetime import datetime

import pygame
from pygame_gui.elements import UIImage
from pygame_gui_extras.app import GuiApp

from applehealthtool.TimeDataGraph import UITimeDataGraph

test_data = [
    {"date": datetime.strptime("2022-08-15 12:49:10", "%Y-%m-%d %H:%M:%S"), "systolic": 120, "diastolic": 75},
    {"date": datetime.strptime("2022-08-15 12:48:05", "%Y-%m-%d %H:%M:%S"), "systolic": 126, "diastolic": 71},
    {"date": datetime.strptime("2022-08-15 12:45:50", "%Y-%m-%d %H:%M:%S"), "systolic": 127, "diastolic": 75},
    {"date": datetime.strptime("2022-08-13 12:28:29", "%Y-%m-%d %H:%M:%S"), "systolic": 125, "diastolic": 76},
    {"date": datetime.strptime("2022-08-13 12:27:18", "%Y-%m-%d %H:%M:%S"), "systolic": 120, "diastolic": 74},
    {"date": datetime.strptime("2022-08-13 12:26:19", "%Y-%m-%d %H:%M:%S"), "systolic": 134, "diastolic": 74},
    {"date": datetime.strptime("2022-08-09 10:44:44", "%Y-%m-%d %H:%M:%S"), "systolic": 125, "diastolic": 77},
    {"date": datetime.strptime("2022-08-09 10:42:50", "%Y-%m-%d %H:%M:%S"), "systolic": 124, "diastolic": 80},
    {"date": datetime.strptime("2022-08-09 10:41:21", "%Y-%m-%d %H:%M:%S"), "systolic": 140, "diastolic": 78},
    {"date": datetime.strptime("2022-08-09 10:39:37", "%Y-%m-%d %H:%M:%S"), "systolic": 150, "diastolic": 80},
    {"date": datetime.strptime("2022-08-07 09:06:30", "%Y-%m-%d %H:%M:%S"), "systolic": 121, "diastolic": 83},
    {"date": datetime.strptime("2022-08-06 11:36:45", "%Y-%m-%d %H:%M:%S"), "systolic": 122, "diastolic": 70},
    {"date": datetime.strptime("2022-08-04 12:17:26", "%Y-%m-%d %H:%M:%S"), "systolic": 134, "diastolic": 79},
    {"date": datetime.strptime("2022-08-04 12:15:11", "%Y-%m-%d %H:%M:%S"), "systolic": 127, "diastolic": 81},
    {"date": datetime.strptime("2022-08-04 12:13:24", "%Y-%m-%d %H:%M:%S"), "systolic": 134, "diastolic": 85},
    {"date": datetime.strptime("2022-07-31 10:26:29", "%Y-%m-%d %H:%M:%S"), "systolic": 124, "diastolic": 72},
    {"date": datetime.strptime("2022-07-31 10:23:41", "%Y-%m-%d %H:%M:%S"), "systolic": 132, "diastolic": 71},
    {"date": datetime.strptime("2022-07-31 10:21:52", "%Y-%m-%d %H:%M:%S"), "systolic": 124, "diastolic": 73},
    {"date": datetime.strptime("2022-07-28 18:33:06", "%Y-%m-%d %H:%M:%S"), "systolic": 121, "diastolic": 76},
    {"date": datetime.strptime("2022-07-28 18:30:52", "%Y-%m-%d %H:%M:%S"), "systolic": 139, "diastolic": 77},
    {"date": datetime.strptime("2022-07-26 16:28:50", "%Y-%m-%d %H:%M:%S"), "systolic": 128, "diastolic": 75},
    {"date": datetime.strptime("2022-07-26 16:25:48", "%Y-%m-%d %H:%M:%S"), "systolic": 121, "diastolic": 76},
    {"date": datetime.strptime("2022-07-16 08:34:42", "%Y-%m-%d %H:%M:%S"), "systolic": 130, "diastolic": 81},
    {"date": datetime.strptime("2022-07-16 08:31:36", "%Y-%m-%d %H:%M:%S"), "systolic": 135, "diastolic": 85},
    {"date": datetime.strptime("2022-07-04 12:06:15", "%Y-%m-%d %H:%M:%S"), "systolic": 134, "diastolic": 75},
    {"date": datetime.strptime("2022-07-04 12:03:08", "%Y-%m-%d %H:%M:%S"), "systolic": 130, "diastolic": 73},
    {"date": datetime.strptime("2022-07-04 12:01:39", "%Y-%m-%d %H:%M:%S"), "systolic": 152, "diastolic": 77},
    {"date": datetime.strptime("2022-06-29 10:53:30", "%Y-%m-%d %H:%M:%S"), "systolic": 123, "diastolic": 73},
    {"date": datetime.strptime("2022-06-16 12:38:14", "%Y-%m-%d %H:%M:%S"), "systolic": 126, "diastolic": 81},
    {"date": datetime.strptime("2022-06-16 12:34:13", "%Y-%m-%d %H:%M:%S"), "systolic": 148, "diastolic": 85},
    {"date": datetime.strptime("2022-06-09 22:39:18", "%Y-%m-%d %H:%M:%S"), "systolic": 146, "diastolic": 85},
    {"date": datetime.strptime("2022-06-01 11:23:04", "%Y-%m-%d %H:%M:%S"), "systolic": 137, "diastolic": 77},
    {"date": datetime.strptime("2022-06-01 10:36:23", "%Y-%m-%d %H:%M:%S"), "systolic": 146, "diastolic": 81},
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
            },
            data=test_data

        )
UIImage
if __name__ == '__main__':
    app = GraphTestApp()
    app.setup()
    app.run()
