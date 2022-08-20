import datetime
import os
import pathlib
import zipfile

import pygame
import pygame_gui
from pygame_gui import UI_FILE_DIALOG_PATH_PICKED
from pygame_gui.elements import UIPanel, UIButton
from pygame_gui.windows import UIFileDialog, UIMessageWindow
from pycraft_gui.gui_app import GuiApp

import applehealthtool
from applehealthtool.data_panel import DataPanel, LOAD_DATABASE, SELECT_DATABASE, SELECT_SOURCE_FILE, LOAD_DATA_SOURCE
from applehealthtool.healthdatabase import AppleHealthDatabase
from applehealthtool.healthdatabase import HealthData
from applehealthtool.report import ReportPanel

import xml.etree.ElementTree as ET

class AppleHealthTool(GuiApp):
    def __init__(self, size=(1280, 960)):
        super().__init__(size, title='Apple Heath Data Tool')
        themes_file = applehealthtool.get_themes_file_path('theme.json')
        print(f'themes file: {themes_file}')
        if themes_file:
            self.ui_manager.get_theme().load_theme(themes_file)
        else:
            print(f'WARNING: theme file not found')
        self._quit_button = None
        self._data_button = None
        self._report_button = None
        self._margin = 2
        self._button_width = 100
        self._button_height = 35
        self._button_rect = pygame.Rect(0, 0, self._button_width, self._button_height)
        self._database = AppleHealthDatabase()

    def setup(self):
        button_pane = UIPanel(
            pygame.Rect(0, 0, self.size[0], self._button_height + (3 * self._margin)), 1,
            anchors={
                'top': 'top', 'left': 'left',
                'bottom': 'top', 'right': 'right'
            },
            margins={'top': self._margin, 'left': self._margin,
                     'bottom': self._margin, 'right': self._margin},
            manager=self.ui_manager
        )
        self._data_button = UIButton(
            self._button_rect,
            'Data',
            manager=self.ui_manager,
            container=button_pane,
            anchors={'top': 'top', 'left': 'left',
                     'bottom': 'top', 'right': 'left'}
        )
        x = self._data_button.get_relative_rect().right
        y = self._data_button.get_relative_rect().top
        self._report_button = UIButton(
            pygame.Rect(x, y,
                        self._button_width, self._button_height),
            'Reports',
            manager=self.ui_manager,
            container=button_pane,
            anchors={'top': 'top', 'left': 'left',
                     'bottom': 'top', 'right': 'left'},
        )
        self._report_button.disable()
        x = -self._button_width
        self._quit_button = UIButton(
            pygame.Rect(x, y, self._button_width, self._button_height),
            'Exit',
            manager=self.ui_manager,
            container=button_pane,
            anchors={
                'top': 'top', 'left': 'right',
                'bottom': 'top', 'right': 'right'
            }
        )
        self._data_button.disable()

        self._report_panel = ReportPanel(
            pygame.Rect(0, button_pane.get_relative_rect().bottom,
                        self.size[0], self.size[1] - button_pane.get_relative_rect().height),
            1,
            anchors={
                'top': 'top', 'left': 'left',
                'bottom': 'bottom', 'right': 'right'
            },
            manager=self.ui_manager,
            visible=False
        )
        self._data_panel = DataPanel(
            pygame.Rect(0, button_pane.get_relative_rect().bottom,
                        self.size[0], self.size[1] - button_pane.get_relative_rect().height),
            1,
            anchors={
                'top': 'top', 'left': 'left',
                'bottom': 'bottom', 'right': 'right'
            },
            manager=self.ui_manager,
        )

    def handle_event(self, event):
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == self._data_button:
                print(f'data button')
                self._report_panel.hide()
                self._data_panel.show()
            elif event.ui_element == self._report_button:
                print(f'report')
                self._report_panel.show()
                self._data_panel.hide()
            elif event.ui_element == self._quit_button:
                print(f'quit')
                self.is_running = False
                pygame.quit()
        elif event.type == LOAD_DATABASE:
            print(f'load database: {event.db_path}')
            self.open_database(event.db_path)
        elif event.type == LOAD_DATA_SOURCE:
            self.open_data_source(event.file_path)
        elif event.type == SELECT_SOURCE_FILE:
            print(f'select source {event}')
            UIFileDialog(
                pygame.Rect(0, 0, 800, 600),
                self.ui_manager,
                'Select Data Source',
                initial_file_path=event.file_path,
                object_id='#data_source_dialog',
                allow_existing_files_only=False
            )
            self._data_panel.disable()
            self._report_panel.disable()
        elif event.type == SELECT_DATABASE:
            print(f'select database {event}')
            dialog = UIFileDialog(
                pygame.Rect(0, 0, 800, 600),
                self.ui_manager,
                'Select Database File',
                initial_file_path=event.db_path,
                object_id='#database_dialog',
                allow_existing_files_only=False
            )
            self._data_panel.disable()
            self._report_panel.disable()
        elif event.type == UI_FILE_DIALOG_PATH_PICKED:
            print(f'USER EVENT: {event}')
            print(f'new path: {event.text}')
            object_ids = event.ui_element.object_ids
            self._data_panel.enable()
            self._report_panel.enable()
            if '#data_source_dialog' in object_ids:
                self._data_panel.data_source_path = event.text
            elif '#database_dialog' in object_ids:
                self._data_panel.database_path = event.text

    def count_records(self):
        if self.db_engine:
            n = self._database.count_rows()
            print(f'database has {n} rows')
            self._data_panel.set_number_of_records_text(n)
            print(f'Most recent: {self._database.latest_record()}')

    def open_database(self, path):
        try:
            if not os.path.exists(os.path.dirname(path)):
                os.makedirs(os.path.dirname(path))
            self.db_engine = self._database.open_database(path)
        except Exception as e:
            print(f'Uh-oh: {e}')
            UIMessageWindow(
                pygame.Rect(10, 10, 600, 300),
                f'{e}'.replace('\n', '<br>'),
                self.ui_manager,
                window_title='Failed to Open DB'
            )
            return
        self._data_panel.set_database_is_open(True)
        self._data_button.enable()
        self._report_button.enable()
        self.count_records()

    def open_data_source(self, file_path):
        print(f'Path: {file_path}')
        path_obj = pathlib.Path(file_path)
        data = None
        self._data_panel.start_reading_data()
        self._main_loop() # run the main loop once to update the screen

        if path_obj.suffix == '.zip':
            with zipfile.ZipFile(file_path, 'r') as zippy:
                with zippy.open('apple_health_export/export.xml') as d:
                    data = d.read()
        elif path_obj.suffix == '.xml':
            with open(file_path, 'r') as d:
                data = d.read()
        latest = self._database.latest_record() if self.db_engine else None
        self._data_panel.finish_reading_data()
        self._main_loop() # run the main loop once to update the screen
        self.load_xml_data(data, latest)

    def load_xml_data(self, data, latest):
        if not data or not self.db_engine:
            # show an error dialog
            return
        print(f'Loading XML Data...')
        self._data_panel.set_xml_load_progress(0)
        self._main_loop()
        root = ET.fromstring(data)
        # root = tree.getroot()
        records = []
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
        import pytz
        def make_datetime(datetime_string):
            format = '%Y-%m-%d %H:%M:%S %z'
            d = datetime.datetime.strptime(datetime_string, format)
            return d
        # tz = pytz.timezone('US/Pacific')
        # latestDate = datetime.datetime.strptime(latest, '%Y-%m-%d %H:%M:%S.000000').replace(tzinfo=tz) if latest else None
        total_records = len(root)
        self._data_panel.set_xml_total_records(total_records)
        n = 0
        for elem in root:
            n += 1
            if elem.tag == 'Record':
                self._data_panel.set_xml_load_progress(n)
                if n % 1000 == 0:
                    self._main_loop()
                creationDate = make_datetime(elem.attrib['creationDate'])
                if latest and creationDate < latest:
                    continue
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
                records.append(record)
        self._data_panel.set_xml_load_progress(total_records)

        total_records = len(records)

        def db_save_progress_callback(n):
            print(f' - progress: {n}')
            self._data_panel.set_database_save_progress(n)
            self._main_loop()

        self._data_panel.set_database_total_records(total_records)
        self._main_loop()
        self._database.insert_records(records, callback=db_save_progress_callback)
        self.count_records()
        return records

