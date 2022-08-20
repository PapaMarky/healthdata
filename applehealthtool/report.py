import pygame
import pygame_gui
from pygame_gui.core import ObjectID
from pygame_gui.elements import UIPanel, UILabel, UIButton

from applehealthtool.blood_pressure import BloodPressureReport


class ReportPanel(UIPanel):
    def __init__(self, *args, **kwargs):
        super(ReportPanel, self).__init__(*args, **kwargs)
        self._button_height = 35
        self._button_width = 150
        x = y = 0
        w = self.get_relative_rect().width
        h = self._button_height
        UILabel(
            pygame.Rect(x, y, w, h),
            'Reports',
            self.ui_manager,
            container=self,
            object_id=ObjectID(class_id='@label_center',
                               object_id='@bold')
        )
        y += self._button_height
        button_panel = UIPanel(
            pygame.Rect(x, y, w, h), 1,
            self.ui_manager,
            container=self,
            anchors={
                'top': 'top', 'left': 'left',
                'bottom': 'top', 'right': 'right'
            }
        )
        x = y = 0
        self.bp_button = UIButton(
            pygame.Rect(x, y, self._button_width, self._button_height),
            'Blood Pressure',
            self.ui_manager, container=button_panel,
            anchors={
                'top': 'top', 'left': 'left',
                'bottom': 'top', 'right': 'left'
            }
        )
        x += self._button_width
        self.other = UIButton(
            pygame.Rect(x, y, self._button_width, self._button_height),
            'Other', self.ui_manager, container=button_panel,
            anchors={
                'top': 'top', 'left': 'left',
                'bottom': 'top', 'right': 'left'
            }
        )
        x = 0
        y = button_panel.get_relative_rect().bottom
        w = self.get_relative_rect().width
        h = self.get_relative_rect().height
        self.bp_panel = BloodPressureReport(
            pygame.Rect(x, y, w, h), 1,
            self.ui_manager,
            container=self,
            anchors={
                'top': 'top', 'left': 'left',
                'bottom': 'top', 'right': 'right'
            }
        )

    def show_panel(self, panel):
        for p in (self.bp_panel,):
            if panel == p:
                p.show()
            else:
                p.hide()

    def process_event(self, event: pygame.event.Event) -> bool:
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == self.bp_button:
                print(f'BP button')
                self.show_panel(self.bp_panel)
            else:
                self.show_panel(None)

