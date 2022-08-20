import pygame
from pygame_gui.core import ObjectID
from pygame_gui.elements import UIPanel, UILabel


class BloodPressureReport(UIPanel):
    def __init__(self, *args, **kwargs):
        super(BloodPressureReport, self).__init__(*args, **kwargs)
        self.hide()
        self._button_height = 35
        self._button_width = 150
        x = y = 0
        w = self.get_relative_rect().width
        h = self._button_height
        UILabel(
            pygame.Rect(x, y, w, h),
            'Blood Pressure',
            self.ui_manager,
            container=self,
            object_id=ObjectID(class_id='@label_center',
                               object_id='@bold')
        )
