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
        'margin': 10,
        'title': {
            'font': 'arial',
            'font_size': 20,
            'text_color': pygame.Color(0, 0, 0)
        },
        'graph': {
            'background_color': pygame.Color(200, 200, 200)
        }
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
                 graph_background = None,
                 data_config=None,
                 data=None
                 ):
        self.background_color = UIGraph.DEFAULT_CONFIG['background_color']
        self._margin = self.DEFAULT_CONFIG['margin']
        self._title = title
        if title_font_name is None:
            title_font_name = self.DEFAULT_CONFIG['title']['font']
        if title_font_size == 0:
            title_font_size = self.DEFAULT_CONFIG['title']['font_size']
        if title_text_color is None:
            self._title_text_color = self.DEFAULT_CONFIG['title']['text_color']

        if graph_background is None:
            self._graph_bg_color = self.DEFAULT_CONFIG['graph']['background_color']

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
        self.recalculate_layout()
        self.redraw()
        # IGraph._list_system_fonts()

    @property
    def top_margin(self):
        return self._margin
    @property
    def bottom_margin(self):
        return self._margin
    @property
    def left_margin(self):
        return self._margin
    @property
    def right_margin(self):
        return self._margin

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

    def recalculate_layout(self):
        width, height = self.get_relative_rect().size

        # for now, title is centered horizontally, top aligned vertically
        w = self._title_image.get_width()
        h = self._title_image.get_height()
        x = self.left_margin + width / 2 - w / 2
        y = self.top_margin
        self._title_rect = pygame.Rect(x, y, w, h)

        # graph box
        w = width - self.left_margin - self.right_margin
        h = height - self.top_margin - self._title_rect.height - self.bottom_margin
        x = self.left_margin
        y = self.top_margin + self._title_rect.height
        self._graph_rect = pygame.Rect(x, y, w, h)

    def draw_title(self, surface):
        # draw the title
        if self._title_image:
            surface.blit(self._title_image, (self._title_rect.left, self._title_rect.top))

    def draw_graph(self, surface):
        # draw the graph
        pygame.draw.rect(surface, self._graph_bg_color, self._graph_rect)

    def redraw(self):
        surface = pygame.Surface(self.get_relative_rect().size, flags=SRCALPHA)
        surface.fill(self._background_color)
        self.draw_title(surface)
        self.draw_graph(surface)
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