from typing import Union, Dict

import pygame
from pygame import SRCALPHA
from pygame_gui.core import IContainerLikeInterface, UIElement, ObjectID
from pygame_gui.core.interfaces import IUIManagerInterface
from pygame_gui.core.utility import premul_alpha_surface
from pygame_gui.elements import UIImage

from applehealthtool.GraphData import DataViewScaler


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
            'background_color': pygame.Color(200, 200, 200),
            'axis': {
                'color': pygame.Color(0, 0, 0),
                'width': 3
            }
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
                 axis_width = None,
                 axis_color = None,
                 graph_background = None,
                 data=None
                 ):
        self.data_sets = []
        for d in data:
            self.add_data(d)

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

        self.axis_color = self.DEFAULT_CONFIG['graph']['axis']['color'] if axis_color is None else axis_color
        self.axis_width = self.DEFAULT_CONFIG['graph']['axis']['width'] if axis_width is None else axis_width

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

    def add_data(self, data_set):
        self.data_sets.append(data_set)

    def recalculate_layout(self):
        screen_width, screen_height = self.get_relative_rect().size

        # for now, title is centered horizontally, top aligned vertically
        w = self._title_image.get_width()
        h = self._title_image.get_height()
        x = self.left_margin + screen_width / 2 - w / 2
        y = self.top_margin
        self.title_rect = pygame.Rect(x, y, w, h)

        # graph box
        w = screen_width - self.left_margin - self.right_margin
        h = screen_height - self.top_margin - self.title_rect.height - self.bottom_margin
        x = self.left_margin
        y = self.top_margin + self.title_rect.height
        self.graph_rect = pygame.Rect(x, y, w, h)

        axis_size = 150 # where this should come from ???
        # y axis box
        w = axis_size
        h = self.graph_rect.height - axis_size
        x = self.graph_rect.left
        y = self.graph_rect.top
        self.y_axis_rect = pygame.Rect(x, y, w, h)
        # x axis box
        w = self.graph_rect.width - axis_size
        h = axis_size
        x = self.graph_rect.left + axis_size
        y = self.graph_rect.bottom - axis_size
        self.x_axis_rect = pygame.Rect(x, y, w, h)

        # graph data display rect
        w = screen_width - axis_size - self.left_margin - self.right_margin
        h = screen_height - axis_size - self.title_rect.height - 2 * self._margin
        x = self.y_axis_rect.right
        y = self.title_rect.bottom
        self.graph_data_rect = pygame.Rect(x, y, w, h)


    def draw_title(self, surface):
        # draw the title
        if self._title_image:
            surface.blit(self._title_image, (self.title_rect.left, self.title_rect.top))

    def draw_graph(self, surface):
        # draw the graph
        pygame.draw.rect(surface, self._graph_bg_color, self.graph_rect)

    def draw_axis(self, surface):
        start = self.y_axis_rect.topright
        end = self.y_axis_rect.bottomright
        pygame.draw.line(surface, self.axis_color, start, end, self.axis_width)
        start = self.x_axis_rect.topleft
        end = self.x_axis_rect.topright
        pygame.draw.line(surface, self.axis_color, start, end, self.axis_width)

    def draw_data_sets(self, surface):
        if len(self.data_sets) < 1:
            return
        (xmin, xmax) = self.data_sets[0].x_minmax
        (ymin, ymax) = self.data_sets[0].y_minmax
        for ds in self.data_sets:
            (xmin1, xmax1) = ds.x_minmax
            if xmin1 < xmin:
                xmin = xmin1
            if xmax1 > xmax:
                xmax = xmax1
            (ymin1, ymax1) = ds.y_minmax
            if ymin1 < ymin:
                ymin = ymin1
            if ymax1 > ymax:
                ymax = ymax1
        view_min_x = self.graph_data_rect.left
        view_max_x = self.graph_data_rect.right
        xscaler = DataViewScaler((xmin, xmax), (view_min_x, view_max_x))
        view_min_y = self.graph_data_rect.top
        view_max_y = self.graph_data_rect.bottom
        yscaler = DataViewScaler((ymin, ymax), (view_min_y, view_max_y))

        for ds in self.data_sets:
            print(f'DS: {ds}')
            lines = []
            ycount = ds.y_per_column
            for y in range(ycount):
                print(f'Start Empty Line: {y}')
                lines.append([])

            for row in ds:
                print(f' - row: {row}')
                x = xscaler.scale(row[0])
                pygame.draw.line(surface, pygame.Color(0, 0, 0), (x, self.graph_data_rect.top), (x, self.graph_data_rect.bottom))
                for i in range(ycount):
                    y = yscaler.scale(row[i + 1])
                    lines[i].append([x, y])

            for line in lines:
                print(f'POINTS: {line}')
                pygame.draw.lines(surface, ds.color, False, line, width=ds.line_width)



    def draw_graph_data(self, surface):
        pygame.draw.rect(surface, pygame.Color(255, 255, 0), self.graph_data_rect)
        self.draw_data_sets(surface)

    def redraw(self):
        surface = pygame.Surface(self.get_relative_rect().size, flags=SRCALPHA)
        surface.fill(self._background_color)
        self.draw_title(surface)
        self.draw_graph(surface)
        self.draw_graph_data(surface)
        self.draw_axis(surface)
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