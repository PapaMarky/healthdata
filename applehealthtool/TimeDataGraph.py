from typing import Union, Dict

import pygame
from pygame import SRCALPHA
from pygame_gui.core import IContainerLikeInterface, UIElement, ObjectID
from pygame_gui.core.interfaces import IUIManagerInterface
from pygame_gui.core.utility import premul_alpha_surface
from pygame_gui.elements import UIImage


class UIGraph(UIImage):
    DEFAULT_CONFIG = {
        'background_color': pygame.Color(255, 255, 255),
        'title_font': 'arial',
        'title_font_size': 20,
        'title_text_color': pygame.Color(0, 0, 0)
    }
    def __init__(self,
                 relative_rect: pygame.Rect,
                 manager: IUIManagerInterface,
                 container: Union[IContainerLikeInterface, None] = None,
                 parent_element: UIElement = None,
                 object_id: Union[ObjectID, str, None] = None,
                 anchors: Dict[str, str] = None,
                 visible: int = 1,
                 title='',
                 title_font_name = None,
                 title_font_size = 0,
                 title_text_color = None,
                 data_config=None,
                 data=None
                 ):
        self.background_color = UIGraph.DEFAULT_CONFIG['background_color']

        self._title = title
        if title_font_name is None:
            title_font_name = self.DEFAULT_CONFIG['title_font']
        if title_font_size == 0:
            title_font_size = self.DEFAULT_CONFIG['title_font_size']
        if title_text_color is None:
            self._title_text_color = self.DEFAULT_CONFIG['title_text_color']

        self.set_title_font(title_font_name, title_font_size)

        self.set_data(data_config, data)
        surface = pygame.Surface(relative_rect.size)
        super().__init__(relative_rect,
                         surface,
                         manager,
                         container=container,
                         parent_element=parent_element,
                         object_id=object_id,
                         anchors=anchors,
                         visible=visible
                         )
        self.redraw()
        # IGraph._list_system_fonts()

    @property
    def background_color(self):
        return self._background_color

    @background_color.setter
    def background_color(self, color):
        self._background_color = color

    @property
    def title_font(self):
        return self._title_font

    def set_title_font(self, font_name, font_size):
        pygame.font.init()
        print(f'title font is {font_name} / {font_size}')
        font_name = pygame.font.SysFont(font_name, font_size)
        self._title_font = font_name
        # pre render the title
        self._title_image = self._title_font.render(self._title, True, self._title_text_color) # self.background_color)
        self._title_image = premul_alpha_surface(self._title_image)
        print(f'title img: {self._title_image}, color: {self.background_color}')

    def set_data(self, config, rows):
        '''
        Set the graph data.

        :param config: dict that maps rows to timestamp, and list of column names to graph as data samples.
            Must contain 'timestamp' and at least one column name.
        :param rows: list of dicts with each dict representing a data sample. Every row must contain all of the columns
            described in config
        :return: None
        '''
        if config is not None:
            assert 'timestamp' in config
            assert 'samples' in config

    def redraw(self):
        surface = pygame.Surface(self.get_relative_rect().size, flags=SRCALPHA)
        surface.fill(self._background_color)

        # draw the title
        if self._title_image:
            surface.blit(self._title_image, (5,5))

        self.set_image(surface)

    @classmethod
    def _list_system_fonts(cls):
        fonts = pygame.font.get_fonts()
        print(len(fonts))
        for f in fonts:
            print(f)


class UITimeDataGraph(UIGraph):
    def __init__(self,
                 relative_rect: pygame.Rect,
                 manager: IUIManagerInterface,
                 container: Union[IContainerLikeInterface, None] = None,
                 parent_element: UIElement = None,
                 object_id: Union[ObjectID, str, None] = None,
                 anchors: Dict[str, str] = None,
                 visible: int = 1,
                 title='',
                 data=None
                 ):
        super().__init__(relative_rect,
                       manager,
                       container=container,
                       parent_element=parent_element,
                       object_id=object_id,
                       anchors=anchors,
                       visible=visible,
                       title=title,
                       data=data
                       )