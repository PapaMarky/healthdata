from typing import Union, Dict

import pygame
from pygame import SRCALPHA
from pygame_gui.core import IContainerLikeInterface, UIElement, ObjectID
from pygame_gui.core.interfaces import IUIManagerInterface
from pygame_gui.core.utility import premul_alpha_surface
from pygame_gui.elements import UIImage

from applehealthtool.GraphData import DataViewScaler, DataSet, DataSeries, DataDateRangeIterator, DataDateRange


class UIGraph(UIImage):
    DEFAULT_CONFIG = {
        'background_color': pygame.Color(255, 255, 255, 255),
        'margin': 10,
        'title': {
            'font': 'arial',
            'font_size': 20,
            'text_color': pygame.Color(0, 0, 0, 255)
        },
        'graph': {
            'background_color': pygame.Color(200, 200, 200, 255),
            'axis': {
                'color': pygame.Color(0, 0, 0, 255),
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
        self.sleep_data = None
        self._xscaler = DataViewScaler([None, None], [None, None])
        self._yscaler = DataViewScaler([0, 200], [None, None])
        if data is not None:
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
        self._surfaces = {}
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

    def add_data(self, data_set:DataSeries):
        self.data_sets.append(data_set)
        xmin, xmax = data_set.x_minmax
        self._xscaler.update_data_limits(xmin, xmax)
        ymin, ymax = data_set.y_minmax
        self._yscaler.update_data_limits(ymin, ymax)

    def add_sleep_data(self, sleep_data:DataDateRange):
        self.sleep_data = sleep_data
        self._xscaler.update_data_limits(sleep_data._xmin, sleep_data._xmax)

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
        self._xscaler.view_min = self.graph_data_rect.left
        self._xscaler.view_max = self.graph_data_rect.right
        self._yscaler.view_min = self.graph_data_rect.bottom
        self._yscaler.view_max = self.graph_data_rect.top

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

    def draw_sleep_data(self, surface):
        if self.sleep_data is None:
            return
        top = self._yscaler.view_max
        bottom = self._yscaler.view_min
        H = bottom - top

        for row in self.sleep_data:
            color = pygame.Color(50, 50, 50, 128)
#           HKCategoryValueSleepAnalysisAsleep
#           HKCategoryValueSleepAnalysisInBed
#           HKCategoryValueSleepAnalysisAwake
            print(f'VAL {row[0]}')
            yoff = 0
            if row[0] == 'HKCategoryValueSleepAnalysisInBed':
                color = pygame.Color(200, 200, 255, 128)
                color2 = pygame.Color(0, 0, 128)
            elif row[0] == 'HKCategoryValueSleepAnalysisAwake':
                color = pygame.Color(255, 255, 200, 128)
                color2 = pygame.Color(128, 128, 0)
                # yoff = H * 0.5
            elif row[0] == 'HKCategoryValueSleepAnalysisAsleep':
                color = pygame.Color(200, 255, 200, 128)
                color2 = pygame.Color(0, 128, 0)
                # yoff = H * 0.75
            left = self._xscaler.scale(row[1])
            right = self._xscaler.scale(row[2])
            w = right - left
            r = pygame.Rect(left, bottom - yoff - H, w, H)
            pygame.draw.rect(surface, color, r)
            #pygame.draw.rect(surface, color2, r, width=1)

    def draw_data_sets(self, surface):
        if len(self.data_sets) < 1:
            return
#       (xmin, xmax) = self.data_sets[0].x_minmax
#       (ymin, ymax) = self.data_sets[0].y_minmax
#       for ds in self.data_sets:
#           if ds.data_count < 1:
#               continue
#           (xmin1, xmax1) = ds.x_minmax
#           if xmin1 < xmin:
#               xmin = xmin1
#           if xmax1 > xmax:
#               xmax = xmax1
#           (ymin1, ymax1) = ds.y_minmax
#           if ymin1 < ymin:
#               ymin = ymin1
#           if ymax1 > ymax:
#               ymax = ymax1

        if not self._yscaler.is_valid or not self._xscaler.is_valid:
            return

        ## Part of BP Data
        y0 = self._yscaler.scale(120) # 120 / 80 : "normal" band for BP
        y1 = self._yscaler.scale(80)
        x0 = self._xscaler.view_min
        x1 = self._xscaler.view_max
        # on the screen zero is top so we put the max world y (200) first to flip the graph
        r = pygame.Rect(x0, y0, x1 - x0, y1 - y0)
        #pygame.draw.rect(surface, pygame.Color(200, 255, 200, 10), r)
        pygame.draw.line(surface, pygame.Color(255, 0, 0, 255),
                         (x0, y0), (x1, y0))
        pygame.draw.line(surface, pygame.Color(0, 0, 200, 255),
                         (x0, y1), (x1, y1))
        for ds in self.data_sets:
            print(f'DS: {ds}')
            lines = []
            ycount = ds.y_per_column
            for y in range(ycount):
                print(f'Start Empty Line: {y}')
                lines.append([])

            if ds.data_count > 0:
                print(f'First Row: {ds._data[0]["startDate"]}')
                print(f' Last Row: {ds._data[-1]["startDate"]}')
            else:
                print(f'NO DATA')
            for row in ds:
                x = self._xscaler.scale(float(row[0]))
                for i in range(ycount):
                    y = self._yscaler.scale(float(row[i + 1]))
                    lines[i].append([x, y])

            for line in lines:
                if len(line) > 1:
                    pygame.draw.lines(surface, ds.color, False, line, width=ds.line_width)

    def draw_graph_data(self, surface):
        # determine over all x and y min/max, create scalers and pass in to draw functions
        pygame.draw.rect(surface, pygame.Color(250, 250, 250, 255), self.graph_data_rect)
        # pygame.draw.rect(surface, pygame.Color(0, 0, 0, 255), self.graph_data_rect, width=1)
        self._surfaces['sleep'] = pygame.Surface(self.get_relative_rect().size, flags=SRCALPHA)

        self.draw_sleep_data(self._surfaces['sleep'])
        # blit the sleep data surface
        surface.blit(self._surfaces['sleep'], (0,0))
        self.draw_data_sets(surface)

    def redraw(self):
        surface = pygame.Surface(self.get_relative_rect().size, flags=SRCALPHA)
        surface.fill(self._background_color)
        self.draw_title(surface)
        self.draw_graph(surface)
        self.draw_axis(surface)
        self.draw_graph_data(surface)
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