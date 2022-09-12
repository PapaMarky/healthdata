import datetime

import pygame


class DataSeries():

    def __init__(self, rows, x_data_row, y_data_rows,
                 label='', color=pygame.Color(0, 0, 0), timeseries=False, line_width=1):
        self._data = rows

        self._x_data_row = x_data_row
        self._y_data_rows = y_data_rows
        self._label = label
        self._color = color
        self._line_width = line_width

        if timeseries:
            # convert dates to integers
            orig_x_col = x_data_row + '_orig'
            print(f'Rename timestamp row to {orig_x_col}')
            for d in self._data:
                d[orig_x_col] = d[x_data_row]
                d[x_data_row] = datetime.datetime.timestamp(d[x_data_row])
                print(f' - timestamp: {d[x_data_row]}')
        self._xmin = self._data[0][self._x_data_row]
        self._xmax = self._data[-1][self._x_data_row]

        self._ymin = self._ymax = self._data[0][self._y_data_rows[0]]
        for row in self._data:
            for col in self._y_data_rows:
                d = row[col]
                if d < self._ymin:
                    self._ymin = d
                if d > self._ymax:
                    self._ymax = d

        print(f'   x min/max: {self._xmin} / {self._xmax}')
        print(f'data min/max: {self._ymin} / {self._ymax}')

    class DataSeriesIterator():
        def __init__(self, dataseries):
            self._series = dataseries
            self._current = 0

        def __next__(self):
            if self._current < len(self._series._data):
                row = [self._series._data[self._current][self._series._x_data_row]]
                for y in self._series._y_data_rows:
                    row.append(self._series._data[self._current][y])
                self._current += 1
                return row
            else:
                raise StopIteration

    def __iter__(self):
        return self.DataSeriesIterator(self)

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
        return len(self._y_data_rows)

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

    def scale(self, data_value):
        if self.clamp:
            if data_value < self.data_min:
                data_value = self.data_min
            elif data_value > self.data_max:
                data_value = self.data_max
        r = (data_value - self.data_min) / (self.data_max - self.data_min)
        return r * (self.view_max - self.view_min) + self.view_min

    @property
    def data_min(self):
        return self.data_limits[0]
    @property
    def data_max(self):
        return self.data_limits[1]
    @property
    def view_min(self):
        return self.view_limits[0]
    @property
    def view_max(self):
        return self.view_limits[1]
