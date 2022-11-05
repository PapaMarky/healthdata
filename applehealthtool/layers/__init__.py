from typing import Union

import pygame
from pygame_gui.core.utility import premul_alpha_surface

from applehealthtool.GraphData import DataViewScaler, DataSet, DataSeries, DataDateRange


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
    def __init__(self, size, bg_color:pygame.Color, xscaler:DataViewScaler, yscaler:DataViewScaler, offset=(0,0)):
        super(BackgroundLayer, self).__init__(offset=offset)
        self.bg_color = bg_color
        self._xscaler = xscaler
        self._yscaler = yscaler
        self._size = size

    def update_surface(self):
        if not self.surface:
            self.surface = pygame.Surface(self._size, flags=pygame.SRCALPHA)

    def update(self):
        self.update_surface()
        if self.surface:
            self.surface.fill(self.bg_color)

class BPRangeLayer(BackgroundLayer):
    def __init__(self,size, color:pygame.Color, xscaler:DataViewScaler, yscaler:DataViewScaler):
        super(BPRangeLayer, self).__init__(size, color, xscaler, yscaler)

    def update(self):
        self.update_surface()
        if not self.dirty or not self.visible:
            return
        y0 = self._yscaler.scale(120) # 120 / 80 : "normal" range for BP
        y1 = self._yscaler.scale(80)
        x0 = self._xscaler.view_min
        x1 = self._xscaler.view_max
        # on the screen zero is top so we put the max world y (200) first to flip the graph
        r = pygame.Rect(x0, y0, x1 - x0, y1 - y0)
        pygame.draw.rect(self.surface, pygame.Color(200, 255, 200, 128), r)
        pygame.draw.line(self.surface, pygame.Color(0, 255, 0, 255), (x0, y0), (x1, y0))
        pygame.draw.line(self.surface, pygame.Color(0, 255, 0, 255), (x0, y1), (x1, y1))

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
        lines = []
        ycount = self.data_set.y_per_column
        for y in range(ycount):
            print(f'Start Empty Line: {y}')
            lines.append([])

        if self.data_set.data_count > 0:
            print(f'First Row: {self.data_set._data[0]["startDate"]}')
            print(f' Last Row: {self.data_set._data[-1]["startDate"]}')
        else:
            print(f'NO DATA')
        for row in self.data_set:
            x = self._xscaler.scale(float(row[0]))
            for i in range(ycount):
                y = self._yscaler.scale(float(row[i + 1]))
                lines[i].append([x, y])

        for line in lines:
            if len(line) > 1:
                pygame.draw.lines(self.surface, self.data_set.color, False, line, width=self.data_set.line_width)

class DateRangeDataLayer(DataSetLayer):
    def __init__(self, data_set, size, xscaler:DataViewScaler, yscaler:DataViewScaler, type_color_map:dict, type_row:int ):
        if not isinstance(data_set, DataDateRange):
            raise Exception('DateRangeDataLayer data_set must be DataDateRange instance')
        self.type_row = type_row
        self.type_color_map = type_color_map
        super(DateRangeDataLayer, self).__init__(data_set, size, xscaler, yscaler)

    def update(self):
        super().update()
        if not self.visible or not self.dirty:
            return

        top = self._yscaler.view_max
        bottom = self._yscaler.view_min
        H = bottom - top
        yoff = 0
        for row in self.data_set:
            color = pygame.Color(255, 0, 255, 255)
            if row[self.type_row] in self.type_color_map:
                color = self.type_color_map[row[self.type_row]]

            left = self._xscaler.scale(row[1])
            right = self._xscaler.scale(row[2])
            w = right - left
            r = pygame.Rect(left, bottom - yoff - H, w, H)
            pygame.draw.rect(self.surface, color, r)
