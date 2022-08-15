import pygame
from pygame_gui.elements import UIPanel, UILabel


class ReportPanel(UIPanel):
    def __init__(self, *args, **kwargs):
        super(ReportPanel, self).__init__(*args, **kwargs)
        self._button_height = 35
        UILabel(
            pygame.Rect(0, 0, self.get_relative_rect().width, self._button_height),
            'Reports',
            self.ui_manager,
            container=self
        )
