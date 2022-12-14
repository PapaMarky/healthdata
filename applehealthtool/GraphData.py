import datetime

import pygame


class DataSet():
    def __init__(self, name, rows, label='', color=pygame.Color(0, 0, 0)):
        self.name = name
        self._data = rows
        self.label = label
        self._color = color

    @property
    def data_count(self):
        return len(self._data)

    def get_iter_row(self, index):
        if index >= 0 and index < self.data_count:
            return []
        raise StopIteration

    class DataSetIterator():
        def __init__(self, rangedata):
            self._series = rangedata
            self._current = 0

        def __next__(self):
            if self._current < len(self._series._data):
                row = self._series.get_iter_row(self._current)
                self._current += 1
                return row
            else:
                raise StopIteration

    def __iter__(self):
        return DataSet.DataSetIterator(self)


class DataDateRange(DataSet):
    def __init__(self, name, rows, x_start_col, x_end_col, type_col,
                 config,
                 label='', color=pygame.Color(200, 200, 255), border_color=None, border_width=0
                 ):
        super().__init__(name, rows, label=label, color=color)
        self.x_start_col = x_start_col
        self.x_end_col = x_end_col
        self.type_col = type_col
        self.config = config
        for t in self.type_col:
            if not t in self.config:
                print(f'WARNING: No entry for {t} in config')
        self._xmin = self._xmax = self._ymin = self._ymax = None
        if self.data_count < 1:
            return
        self._convert_date_cols()

    def _convert_date_cols(self):
        if self.data_count < 1:
            return
        orig_x_start_col = self.x_start_col + '_orig'
        orig_x_end_col = self.x_end_col + '_orig'
        print(f'Rename timestamp row to {orig_x_start_col}')
        for d in self._data:
            d[orig_x_start_col] = d[self.x_start_col]
            d[self.x_start_col] = datetime.datetime.timestamp(d[self.x_start_col])
            d[orig_x_end_col] = d[self.x_end_col]
            d[self.x_end_col] = datetime.datetime.timestamp(d[self.x_end_col])
        self._xmin = float(self._data[0][self.x_start_col])
        self._xmax = float(self._data[-1][self.x_end_col])

    def get_iter_row(self, index):
        if index >= 0 and index < self.data_count:
            return [
                self._data[index][self.type_col],
                self._data[index][self.x_start_col],
                self._data[index][self.x_end_col],
            ]
        else:
            raise StopIteration



class DataSeries(DataSet):

    def __init__(self, name, rows, x_data_col, y_data_cols,
                 label='', color=pygame.Color(0, 0, 0), timeseries=False, line_width=1):
        super().__init__(name, rows, label=label, color=color)

        self._x_data_col = x_data_col
        self._y_data_cols = y_data_cols
        self._line_width = line_width
        self._xmin = self._xmax = self._ymin = self._ymax = None
        if self.data_count < 1:
            return
        if timeseries:
            # convert dates to integers
            orig_x_col = x_data_col + '_orig'
            print(f'Rename timestamp row to {orig_x_col}')
            for d in self._data:
                d[orig_x_col] = d[x_data_col]
                d[x_data_col] = datetime.datetime.timestamp(d[x_data_col])
                # print(f' - timestamp: {d[x_data_row]}')
        self._xmin = float(self._data[0][self._x_data_col])
        self._xmax = float(self._data[-1][self._x_data_col])

        self._ymin = self._ymax = float(self._data[0][self._y_data_cols[0]])
        for row in self._data:
            for col in self._y_data_cols:
                d = float(row[col])
                if d < self._ymin:
                    self._ymin = d
                if d > self._ymax:
                    self._ymax = d

        print(f'   x min/max: {self._xmin} / {self._xmax}')
        print(f'data min/max: {self._ymin} / {self._ymax}')

    def get_iter_row(self, index):
        if index >= 0 and index < self.data_count:
            row = [
                self._data[index][self._x_data_col]
            ]
            for y in self._y_data_cols:
                row.append(self._data[index][y])
            return row
        else:
            raise StopIteration

    @property
    def x_minmax(self):
        return (self._xmin, self._xmax)

    @property
    def y_minmax(self):
        return (self._ymin, self._ymax)

    @property
    def x_min(self):
        return self._xmin

    @property
    def x_max(self):
        return self._xmax

    @property
    def y_min(self):
        return self._ymin

    @property
    def y_max(self):
        return self._ymax

    @property
    def y_per_column(self):
        return len(self._y_data_cols)

    @property
    def color(self):
        return self._color

    @property
    def line_width(self):
        return self._line_width


class DataViewScaler:
    def __init__(self, data_limits, view_limits, clamp=False):
        self.data_limits = data_limits
        self.view_limits = view_limits
        self.clamp = clamp

    def update_view_limits(self, view_min, view_max):
        if self.view_limits is None:
            self.view_limits = [None, None]
        if self.view_min is None or view_min < self.view_min:
            self.view_min = view_min
        if self.view_max is None or view_max > self.view_max:
            self.view_max = view_max

    def update_data_limits(self, data_min, data_max):
        if self.data_limits is None:
            self.data_limits = [None, None]
        if self.data_min is None or data_min < self.data_min:
            self.data_min = data_min
        if self.data_max is None or data_max > self.data_max:
            self.data_max = data_max

    def scale(self, data_value):
        data_value = float(data_value)
        if self.clamp:
            if data_value < self.data_min:
                data_value = self.data_min
            elif data_value > self.data_max:
                data_value = self.data_max
        r = (data_value - self.data_min) / (self.data_max - self.data_min)
        return r * (self.view_max - self.view_min) + self.view_min

    @property
    def is_valid(self):
        if self.data_min is None or self.data_max is None or self.view_min is None or self.view_max is None:
            return False
        return True

    @property
    def data_min(self):
        return self.data_limits[0]

    @data_min.setter
    def data_min(self, value):
        self.data_limits[0] = value

    @property
    def data_max(self):
        return self.data_limits[1]

    @data_max.setter
    def data_max(self, value):
        self.data_limits[1] = value

    @property
    def view_min(self):
        return self.view_limits[0]

    @view_min.setter
    def view_min(self, value):
        self.view_limits[0] = value

    @property
    def view_max(self):
        return self.view_limits[1]

    @view_max.setter
    def view_max(self, value):
        self.view_limits[1] = value
