from typing import Union, Dict

import pygame
from pygame import SRCALPHA
from pygame_gui.core import IContainerLikeInterface, UIElement, ObjectID
from pygame_gui.core.interfaces import IUIManagerInterface
from pygame_gui.elements import UIImage

from applehealthtool.GraphData import DataViewScaler, DataSeries, DataDateRange
from applehealthtool.layers import TextLayer, BackgroundLayer, AxisLayer, BPRangeLayer, GraphLayer, DataSeriesLayer, \
    DateRangeDataLayer


class UIGraph(UIImage):
    DEFAULT_CONFIG = {
        'background_color': pygame.Color(220, 220, 220, 255),
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
                 graph_background = None
                 ):
        self.data_sets = []
        self._layer_list = []
        self.sleep_data = None
        self._xscaler = DataViewScaler([None, None], [None, None])
        self._yscaler = DataViewScaler([0, 200], [None, None])

        self._background_color = UIGraph.DEFAULT_CONFIG['background_color']
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

        # self.set_title_font(title_font_name, title_font_size)

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

        self.title_layer = TextLayer(title, font_name=title_font_name, font_size=title_font_size, color=title_text_color)
        self.title_layer.update() # need to create text surface before recalulate_layout
        self.add_layer(self.title_layer)

        self.calculate_graph_rect()
        origin = self.graph_rect.topleft
        self.background_layer = BackgroundLayer(self.graph_rect.size, pygame.Color(220, 220, 220, 255), self._xscaler, self._yscaler, offset=origin)
        self.add_layer(self.background_layer)

        self.axis_layer = AxisLayer(self.get_relative_rect().size, self.axis_color, self.axis_width, self._xscaler, self._yscaler, self.graph_rect)
        self.axis_layer.recalculate_layout()

        w = self.graph_rect.width - self.axis_layer.y_axis_rect.width
        h = self.graph_rect.height - self.axis_layer.x_axis_rect.height
        data_bg_layer = BackgroundLayer((w, h), pygame.Color(255, 255, 255, 255), self._xscaler, self._yscaler, self.axis_layer.y_axis_rect.topright)
        self.add_layer(data_bg_layer)

        self.add_layer(self.axis_layer)

        bp_range_layer = BPRangeLayer(self.get_relative_rect().size, pygame.Color(220, 255, 220, 128), self._xscaler, self._yscaler)
        self.add_layer(bp_range_layer)

        self.recalculate_layout()
        # self.redraw()
        # IGraph._list_system_fonts()

    def save_to_image(self, outpath):
        pygame.image.save(self.base_surface, outpath)

    @property
    def base_surface(self):
        return self.image

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

    def add_layer(self, layer:GraphLayer):
        self._layer_list.append(layer)

    def add_data_series_layer(self, data_series:DataSeries):
        xmin, xmax = data_series.x_minmax
        self._xscaler.update_data_limits(xmin, xmax)
        ymin, ymax = data_series.y_minmax
        self._yscaler.update_data_limits(ymin, ymax)
        layer = DataSeriesLayer(data_series, self.get_relative_rect().size, self._xscaler, self._yscaler)
        self._layer_list.append(layer)
        for layer in self._layer_list:
            # If we update the scalers, we need to mark all of the layers as dirty
            layer.dirty = True

    def add_sleep_data(self, sleep_data:DataDateRange):
        self.sleep_data = sleep_data
        self._xscaler.update_data_limits(sleep_data._xmin, sleep_data._xmax)
        TYPE_ROW=0
        type_color_map = {
            'HKCategoryValueSleepAnalysisInBed': pygame.Color(200, 200, 255, 128),
            'HKCategoryValueSleepAnalysisAwake': pygame.Color(255, 255, 200, 128),
            'HKCategoryValueSleepAnalysisAsleep': pygame.Color(200, 255, 200, 128)
        }
        layer = DateRangeDataLayer(sleep_data, self.get_relative_rect().size, self._xscaler, self._yscaler, type_color_map, TYPE_ROW)
        self.add_layer(layer)
        for layer in self._layer_list:
            # If we update the scalers, we need to mark all of the layers as dirty
            layer.dirty = True

    def calculate_title_rect(self):
        # for now, title is centered horizontally, top aligned vertically
        screen_width, screen_height = self.get_relative_rect().size
        w = self.title_layer.surface.get_width()
        h = self.title_layer.surface.get_height()
        x = self.left_margin + screen_width / 2 - w / 2
        y = self.top_margin
        self.title_rect = pygame.Rect(x, y, w, h)
        self.title_layer.offset = (x, y)

    def calculate_graph_rect(self):
        self.calculate_title_rect()
        # graph box
        screen_width, screen_height = self.get_relative_rect().size
        w = screen_width - self.left_margin - self.right_margin
        h = screen_height - self.top_margin - self.title_rect.height - self.bottom_margin
        x = self.left_margin
        y = self.top_margin + self.title_rect.height
        self.graph_rect = pygame.Rect(x, y, w, h)

    def recalculate_layout(self):
        self.calculate_graph_rect()

        # graph data display rect
        screen_width, screen_height = self.get_relative_rect().size
        w = screen_width - self.axis_layer.axis_size - self.left_margin - self.right_margin
        h = screen_height - self.axis_layer.axis_size - self.title_rect.height - 2 * self._margin
        x = self.axis_layer.y_axis_rect.right
        y = self.title_rect.bottom
        self.graph_data_rect = pygame.Rect(x, y, w, h)
        self._xscaler.view_min = self.graph_data_rect.left
        self._xscaler.view_max = self.graph_data_rect.right
        self._yscaler.view_min = self.graph_data_rect.bottom
        self._yscaler.view_max = self.graph_data_rect.top

        for ds in self.data_sets:
            ds_name = ds.name
            if not self._layers[ds_name].visible:
                continue
            print(f'DS: {ds.name}')
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
                    pygame.draw.lines(self._layers[ds.name].surface, ds.color, False, line, width=ds.line_width)

    def draw_graph_data(self):
        pass
#        if not self._layers['graph_rect'].visible:
#            return
#        surface = self._layers['graph_rect'].surface
#
#        # determine over all x and y min/max, create scalers and pass in to draw functions
#        ## TODO Make "draw_sleep_data" function
#        pygame.draw.rect(surface, pygame.Color(250, 250, 250, 255), self.graph_data_rect)

        # self.draw_sleep_data_layer()
        # blit the sleep data surface
        # surface.blit(self._layers['sleep'].surface, (0,0))
        # self.draw_data_sets()

    def redraw(self):
        surface = self.base_surface
        if not surface:
            print(f'Creating missing base surface')
            pygame.Surface(self.get_relative_rect().size, flags=SRCALPHA)
        surface.fill(self._background_color)

        for layer in self._layer_list:
            layer.redraw(self.base_surface)

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
                 title=''
                 ):
        super().__init__(relative_rect,
                       manager,
                       container=container,
                       parent_element=parent_element,
                       object_id=object_id,
                       anchors=anchors,
                       visible=visible,
                       title=title
                       )
