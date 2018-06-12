from PyQt5 import QtGui, QtWidgets, uic, QtCore, Qt

from utils.hapiest_util import *
from PyQt5.QtChart import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from utils.log import *
from utils.graph_type import GraphType
from widgets.gui import GUI
from random import randint
from typing import *
import re
import json

class GraphDisplayWindowGui(GUI, QtWidgets.QMainWindow):

    @staticmethod
    def generate_random_color(r, g, b):
        """
        @returns a tuple, containing 3 integers between 0 and 255 which represent the r, g, and b values of a color.
        """
        return ((randint(0, 255) + r) / 2, (randint(0, 255) + g) / 2, (randint(0, 255) + b) / 2)

    def __init__(self, ty: GraphType, window_title: str):
        QtWidgets.QMainWindow.__init__(self)
        GUI.__init__(self)

        self.graph_ty = ty

        uic.loadUi('layouts/graph_display_window_v2.ui', self)
        self.chart = None
        self.chart_view = None

        self.view_fit.triggered.connect(self.__on_view_fit_triggered)
        
        self.xmax.setKeyboardTracking(False)
        self.xmin.setKeyboardTracking(False)
        self.ymax.setKeyboardTracking(False)
        self.ymin.setKeyboardTracking(False)

        self.xmax.valueChanged.connect(self.__on_xmax_changed)
        self.xmin.valueChanged.connect(self.__on_xmin_changed)
        self.ymax.valueChanged.connect(self.__on_ymax_changed)
        self.ymin.valueChanged.connect(self.__on_ymin_changed)
        
        self.save_as_csv.triggered.connect(self.__on_save_as_csv_triggered)
        self.save_as_json.triggered.connect(self.__on_save_as_json_triggered)
        self.save_as_txt.triggered.connect(self.__on_save_as_txt_triggered)
        self.save_as_png.triggered.connect(self.__on_save_as_png_triggered)

        self.grabGesture(QtCore.Qt.PanGesture)
        self.grabGesture(QtCore.Qt.PinchGesture)

        self.axisy = None
        self.axisx = None
        self.view_xmin = None
        self.view_xmax = None
        self.view_ymin = None
        self.view_ymax = None
        self.chart = None
            
        self.set_chart_title(window_title)

        self.show()


    def set_chart_title(self, title):
        self.setWindowTitle(str(title))


    def add_graph(self, x, y, title, xtitle, ytitle, name, args):
        if self.chart == None:
            series = QLineSeries()
            for i in range(0, x.size):
                series.append(x[i], y[i])
            self.series = [series]
            series.setName( name + ' -<br>Function: {},<br>T: {:.2f} K, P: {:.2f} atm<br>γ-air: {:.2f}, γ-self: {:.2f}'.format(
                args['graph_fn'], args['Environment']['T'], args['Environment']['p'],
                args['Diluent']['air'], args['Diluent']['self']))

            series.setUseOpenGL(True)

            self.chart = QChart()
            self.chart.addSeries(series)
            self.chart.setTitle(title)
            self.setWindowTitle(title)
            # self.chart.legend().setAlignment(QtCore.Qt.AlignRight)

            if self.axisy:
                self.chart.removeAxis(self.axisy)
                self.chart.removeAxis(self.axisx)

            self.axisx = QValueAxis()
            self.axisx.setTickCount(5)
            self.axisx.setTitleText(xtitle)
            self.chart.addAxis(self.axisx, QtCore.Qt.AlignBottom)
            self.series[0].attachAxis(self.axisx)

            self.axisy = QValueAxis()
            self.axisy.setTitleText(ytitle)
            self.axisy.setTickCount(5)
            self.chart.addAxis(self.axisy, QtCore.Qt.AlignLeft)
            self.series[0].attachAxis(self.axisy)
            
            self.chart.legend()
            self.chart_view = QChartView(self.chart)
            self.chart_view.setRubberBand(QChartView.RectangleRubberBand)
            self.chart_view.setRenderHint(QtGui.QPainter.Antialiasing)

            layout = QtWidgets.QGridLayout()
            layout.addWidget(self.chart_view)
            self.loading_label.setDisabled(True)
            self.graph_container.setLayout(layout)
        else:
            series = QLineSeries()
            series.setName( name + ' -<br>Function={},<br>T={:.2f}, P={L.2f}<br>γ-air: {:.2f}, γ-self: {:.2f}'.format(
                args['graph_fn'], args['Environment']['T'], args['Environment']['p'],
                args['Diluent']['air'], args['Diluent']['self']))
            series.setUseOpenGL(True)
            for i in range(0, x.size):
                series.append(x[i], y[i])
            self.chart.addSeries(series)
            series.attachAxis(self.axisy)
            series.attachAxis(self.axisx)
            self.series.append(series)

        if self.view_xmin:
            if self.view_xmin > x[0]:
                self.view_xmin = x[0]
        else:
            self.view_xmin = self.axisx.min()
        if self.view_ymin:
            ymin = min(y)
            if self.view_ymin > ymin:
                self.view_ymin = ymin
        else:
            self.view_ymin = self.axisy.min()

        if self.view_xmax:
            if self.view_xmax < x[len(x) - 1]:
                self.view_xmax = x[len(x) - 1]
        else:
            self.view_xmax = self.axisx.max()
        if self.view_ymax:
            ymax = max(y)
            if self.view_ymax < ymax:
                self.view_ymax = ymax
        else:
            self.view_ymax = self.axisy.max()
        self.__on_view_fit_triggered(True)
        
    def __on_view_fit_triggered(self, _checked: bool):
        """
        Sets the screen focus to maximum values of y and x for series in the graph. The xmin / ymin variables
        are kept track of in such a way where they will always have the most extreme valid values, so using those
        to define the range works to fit the view

        """
        if self.chart:
            self.axisx.setRange(self.view_xmin, self.view_xmax)
            self.axisy.setRange(self.view_ymin, self.view_ymax)

    def __on_xmax_changed(self, value):
        """
        *Params: self, value. Checks to make sure that the values are proper. If the value passed in is
        smaller than the already established x min value, then the x min value is set to be the value -1 and the x max is set to be value passed into the method
        """
        return
        min = self.xmin.value()
        if value < min:
            self.xmax.setValue(value)
            self.xmin.setValue(value - 1)
        self.__on_viewport_changed(True)

    def __on_xmin_changed(self, value):
        """
        *If the value of the number passed in is larger than the currently established max value for x, then the min value is set to be the value passed in , and the max is set to be the value passed into the method + 1.*
        """
        return
        max = self.xmax.value()
        if value > max:
            self.xmin.setValue(value)
            self.xmax.setValue(value + 1)
        self.__on_viewport_changed()

    def __on_ymax_changed(self, value):
        """
        *Sets the value for y max, if the value passed in is smaller than the current y min, then the y max is set to y min, and y min is set to the value passed into the method .*
        """
        return
        min = self.ymin.value()
        if value < min:
            self.ymax.setValue(min)
            self.ymin.setValue(value)
        self.__on_viewport_changed()

    def __on_ymin_changed(self, value):
        """
        *Sets the value for y min, if the value passed in is larger than current y max, then the value of y min is set to be the value of y max, and the y max value is set as the value passed into the method.*
        """
        return
        max = self.ymax.value()
        if value > max:
            self.ymin.setValue(max)
            self.ymax.setValue(value)
        self.__on_viewport_changed()

    def __on_viewport_changed(self):
        """
        *Handles the changing in a viewport for graphing view .*
        """
        if self.chart == None:
            return

        xmin = self.xmin.value()
        xmax = self.xmax.value()
        ymin = self.ymin.value()
        ymax = self.ymax.value()

        if xmin == xmax or ymin == ymax:
            return
        if xmin > xmax:
            t = xmin
            xmin = xmax
            xmax = t
            self.xmin.setValue(xmin)
            self.xmax.setValue(xmax)
        if ymin > ymax:
            t = ymin
            ymin = ymax
            ymax = t
            self.ymin.setValue(ymin)
            self.xmin.setValue(ymax)

        self.axisx.setRange(xmin, xmax)
        self.axisy.setRange(ymin, ymax)

    def get_file_save_name(self, extension, filter) -> Union[str, None]:
        filename = QtWidgets.QFileDialog.getSaveFileName(self, "Save as", "./data" + extension, filter)
        if filename[0] == "":
            return None
        else:
            return str(filename[0])
    
    def __on_save_as_png_triggered(self, _checked: bool):
        if self.chart == None:
            return
        
        filename = self.get_file_save_name('.png', 'PNG files (*.png, *.PNG)')
        
        geometry = self.chart_view.geometry()
        pixmap = QPixmap(16 * geometry.width(), 16 * geometry.height())
        painter = QPainter()
        
        painter.begin(pixmap)
        self.chart_view.render(painter)
        painter.end()

        pixmap.save(filename, 'PNG')

    def __on_save_as_txt_triggered(self, _checked: bool):
        if self.chart == None:
            return

        filename = self.get_file_save_name(".txt", "Text files (*.txt)")

        if filename == None:
            return
        
        try:
            for i in range(0, len(self.series)):
                ith_filename = '{}_{}.txt'.format(filename, i)
                with open(ith_filename, "w") as file:
                    for point in self.series[i].pointsVector():
                        file.write('{:<16.8f}{:.8f}\n'.format(point.x(), point.y()))
                        
        except Exception as e:
            print("Encountered error {} while saving to file".format(str(e)))
    
    def __on_save_as_json_triggered(self, _checked: bool):
        if self.chart == None:
            return

        filename = self.get_file_save_name(".json", "Javascript object notation files (*.json)")
        if filename == None:
            return
        def filter_series_name(s):
            return s.replace('<br>', ' ').replace('γ', 'gamma')
        dict = {}
        series_lists = list(map(lambda series: dict.update({
            filter_series_name(series.name()): 
                list(map(lambda point: [point.x(), point.y()], series.pointsVector())) }), self.series)) 
        try:
            with open(filename, 'w') as file:
                file.write(json.dumps(dict, indent=4))
        except Exception as e:
            print("Encountered error {} while saving to file".format(str(e)))

    def __on_save_as_csv_triggered(self, _checked: bool):
        if self.chart == None:
            return

        filename = self.get_file_save_name(".csv", "Comma separated value files (*.csv)")
        
        if filename == None:
            return 
        
        try:
            point_vectors = []
            for i in range(0, len(self.series)):
                point_vectors.append(self.series[i].pointsVector())
            max_len = max(map(len, point_vectors))
            with open(filename, "w") as file:
                for point_index in range(0, max_len):
                    s = ''
                    for i in range(0, len(self.series)):
                        if point_index >= len(point_vectors[i]):
                            s = '{} {:14s}, {:14s},'.format(s, '', '')
                        else:
                            point = point_vectors[i][point_index]
                            s = '{} {:14s}, {:14s},'.format(s, str(point.x()), str(point.y()))
                    
                    file.write('{}\n'.format(s))
                        
        except Exception as e:
            print("Encountered error {} while saving to file".format(str(e)))
