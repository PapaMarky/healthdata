from typing import Union, Dict

import pygame
from pygame import SRCALPHA
from pygame_gui.core import IContainerLikeInterface, UIElement, ObjectID
from pygame_gui.core.interfaces import IUIManagerInterface
from pygame_gui.core.utility import premul_alpha_surface
from pygame_gui.elements import UIImage

from applehealthtool.GraphData import DataViewScaler, DataSet, DataSeries, DataDateRangeIterator, DataDateRange

class BadArgException(Exception):
    def __init__(self, message='Bad Argument'):
        super().__init__(message)
class BadOffsetException(BadArgException):
    def __init__(self):
        super(BadOffsetException, self).__init__('Offset must be list or tuple with exactly two elements')

class GraphLayer:
    def __init__(self, visible=True, offset=(0,0)):
        self._surface = None
        self.visible = visible
        self.dirty = True
        self._offset = offset
        self._size =None

    def blit(self, target:pygame.Surface):
        if self.visible and self.surface:
            target.blit(self.surface, self._offset)

    def redraw(self, base_surface:pygame.Surface):
        '''
        Update the Layer's surface (if necessary) and blit onto target surface.
        :param base_surface:
        :return:
        '''
        if self.visible:
            if self.dirty:
                self.update()
            self.blit(base_surface)

    def update(self):
        pass # overload this function

    @property
    def ready_to_draw(self):
        return self.surface and self.visible and self.dirty

    @property
    def offset(self):
        return self._offset

    @offset.setter
    def offset(self, offset):
        if offset is None:
            offset = (0, 0)
        # TODO make sure it's a list / tuple of len 2
        print(f'OFFSET: {offset}, TYPE: {type(offset)}')
        if not (type(offset) is list or type(offset) is tuple):
            raise BadOffsetException()
        if len(offset) != 2:
            raise BadOffsetException()
        self._offset = offset

    @property
    def surface(self):
        return self._surface

    @surface.setter
    def surface(self, new_surface:pygame.Surface):
        self._surface = new_surface
        self.dirty = True

class TextLayer(GraphLayer):
    def __init__(self, text:str, font_name:str= '', visible=True, font_size:int=10, color:pygame.Color=None, offset:Union[tuple, list, None]=None):
        super(TextLayer, self).__init__(offset=offset, visible=visible)
        self.offset = offset
        self._text:str = ''
        self.text = text
        self.color = color if color is not None else pygame.Color(0, 0, 0, 255)
        self._font:pygame.font = None
        self._image:pygame.surface = None
        self.set_font(font_name, font_size)

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, text):
        self._text = text
        self.dirty = True

    def set_font(self, name:str, size:int):
        pygame.font.init()
        self._font = pygame.font.SysFont(name, size)
        self.dirty = True

    def update(self):
        if self.visible and self.dirty:
            image = self._font.render(self.text, True, self.color)
            self._surface = premul_alpha_surface(image)
            self.dirty = False


class BackgroundLayer(GraphLayer):
    def __init__(self, size, bg_color:pygame.Color, xscaler:DataViewScaler, yscaler:DataViewScaler):
        super(BackgroundLayer, self).__init__()
        self.bg_color = bg_color
        self._xscaler = xscaler
        self._yscaler = yscaler
        self._size = size

    def update_surface(self):
        if not self.surface:
            self.surface = pygame.Surface(self._size, flags=SRCALPHA)

    def update(self):
        self.update_surface()
        if self.surface:
            self.surface.fill(self.bg_color)

class AxisLayer(BackgroundLayer):
    def __init__(self, size, color:pygame.Color, width:int, xscaler:DataViewScaler, yscaler:DataViewScaler, graph_rect):
        super(AxisLayer, self).__init__(size, pygame.Color(0,0,0,0), xscaler=xscaler, yscaler=yscaler)
        self.axis_size = 150# where this should come from ???
        self.axis_color = color
        self.axis_width = width
        self.graph_rect = graph_rect

    def recalculate_layout(self):
        # y axis box
        w = self.axis_size
        h = self.graph_rect.height - self.axis_size
        x = self.graph_rect.left
        y = self.graph_rect.top
        self.y_axis_rect = pygame.Rect(x, y, w, h)
        # x axis box
        w = self.graph_rect.width - self.axis_size
        h = self.axis_size
        x = self.graph_rect.left + self.axis_size
        y = self.graph_rect.bottom - self.axis_size
        self.x_axis_rect = pygame.Rect(x, y, w, h)

    def update(self):
        super(AxisLayer, self).update()
        if self.visible and self.dirty:
            self.recalculate_layout()
            start = self.y_axis_rect.topright
            end = self.y_axis_rect.bottomright
            pygame.draw.line(self.surface, self.axis_color, start, end, self.axis_width)
            start = self.x_axis_rect.topleft
            end = self.x_axis_rect.topright
            pygame.draw.line(self.surface, self.axis_color, start, end, self.axis_width)

class DataSetLayer(BackgroundLayer):
    def __init__(self, data_set:DataSet, size, xscaler:DataViewScaler, yscaler:DataViewScaler):
        super(DataSetLayer, self).__init__(size, pygame.Color(0,0,0,0), xscaler, yscaler)
        self.data_set = data_set

    @property
    def name(self):
        if self.data_set:
            return self.data_set.name
        return None

class DataSeriesLayer(DataSetLayer):
    def __init__(self, data_set, size, xscaler:DataViewScaler, yscaler:DataViewScaler):
        if not isinstance(data_set, DataSeries):
            raise Exception('DataSeriesLayer data_set must be DataSeries instance')
        super(DataSeriesLayer, self).__init__(data_set, size, xscaler, yscaler)

    def update(self):
        super().update()
        ds = self.data_set
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
                pygame.draw.lines(self.surface, ds.color, False, line, width=ds.line_width)

class DateRangeDataLayer(DataSetLayer):
    def __init__(self, data_set, size):
        if not isinstance(data_set, DataDateRange):
            raise Exception('DateRangeDataLayer data_set must be DataDateRange instance')
        super(DateRangeDataLayer, self).__init__(data_set, size)

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
                 graph_background = None
                 ):
        self.data_sets = []
        self._layer_list = []
        self.sleep_data = None
        self._xscaler = DataViewScaler([None, None], [None, None])
        self._yscaler = DataViewScaler([0, 200], [None, None])

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

        self.background_layer = BackgroundLayer(self.get_relative_rect().size, pygame.Color(255, 128, 128, 128), self._xscaler, self._yscaler)
        self.add_layer(self.background_layer)

        self.calculate_graph_rect()
        self.axis_layer = AxisLayer(self.get_relative_rect().size, self.axis_color, self.axis_width, self._xscaler, self._yscaler, self.graph_rect)
        self.add_layer(self.axis_layer)
        self.axis_layer.recalculate_layout()

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

    @property
    def background_color(self):
        return self._background_color

    @background_color.setter
    def background_color(self, color):
        self._background_color = color

#    @property
#    def title_font(self):
#        return self._title_font
#
#    def set_title_font(self, font_name, font_size):
#        pygame.font.init()
#        print(f'title font is {font_name} / {font_size}')
#        font_name = pygame.font.SysFont(font_name, font_size)
#        self._title_font = font_name
#        # pre render the title
#        self._title_image = self._title_font.render(self._title, True, self._title_text_color) # self.background_color)
#        self._title_image = premul_alpha_surface(self._title_image)
#        print(f'title img: {self._title_image}, color: {self.background_color}')
#
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

    def draw_sleep_data_layer(self):
#        if not self._layers['sleep'].visible:
#            return
#        surface = self._layers['sleep'].surface

        if self.sleep_data is None:
            return
        surface = None
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

    def draw_data_sets(self):
        if len(self.data_sets) < 1:
            return

        if not self._yscaler.is_valid or not self._xscaler.is_valid:
            return


        ## Part of BP Data
        if self._layers['bp_normal'].visible:
            surface = self._layers['bp_normal'].surface
            y0 = self._yscaler.scale(120) # 120 / 80 : "normal" band for BP
            y1 = self._yscaler.scale(80)
            x0 = self._xscaler.view_min
            x1 = self._xscaler.view_max
            # on the screen zero is top so we put the max world y (200) first to flip the graph
            r = pygame.Rect(x0, y0, x1 - x0, y1 - y0)
            pygame.draw.rect(surface, pygame.Color(200, 255, 200, 128), r)
            #pygame.draw.rect(surface, pygame.Color(255, 0, 0, 255), r, width=1)
            pygame.draw.line(surface, pygame.Color(0, 255, 0, 255), (x0, y0), (x1, y0))
            pygame.draw.line(surface, pygame.Color(0, 255, 0, 255), (x0, y1), (x1, y1))
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
        self.draw_data_sets()

    def redraw(self):
        surface = self.base_surface
        if not surface:
            print(f'Creating missing base surface')
            pygame.Surface(self.get_relative_rect().size, flags=SRCALPHA)
        surface.fill(self._background_color)

        self.draw_graph_data()

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
