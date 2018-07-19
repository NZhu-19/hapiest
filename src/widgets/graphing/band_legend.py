from typing import List

from PyQt5.QtCore import *
from PyQt5.QtChart import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import QFrame, QWidget, QHBoxLayout, QLabel, QVBoxLayout, QCheckBox, QScrollArea, QSizePolicy

from utils.graphing.hapi_series import HapiSeries
from utils.hapiest_util import *


class LegendItem(QFrame):

    SELECTED_WIDTH = 8
    NORMAL_WIDTH = 2


    def __init__(self, bands: List[HapiSeries], name, chart):
        QFrame.__init__(self)

        self.chart = chart
        self.bands = bands

        self.band_layouts = []

        def band_hide_function_gen(band):
            def hide(checked):
                band.setVisible(not checked)
            return hide

        for band in self.bands:
            color_indicator = QWidget()
            color_indicator.setFixedSize(24, 24)
            color_indicator.setStyleSheet("""
            QWidget {{
                background-color: #{:x};
                border: 1px solid black;
            }}
            """.format(band.color().rgb()))

            toggle = QCheckBox()
            toggle.toggled.connect(band_hide_function_gen(band))

            label = QLabel(band.series.name())

            layout = QHBoxLayout()

            layout.addWidget(toggle)
            layout.addWidget(color_indicator)
            layout.addWidget(label)

            self.band_layouts.append({
                'label': label,
                'layout': layout,
                'toggle': toggle,
                'color_indicator': color_indicator
            })

        self.toggle_all_layout = QHBoxLayout()
        self.toggle_all = QCheckBox()

        def on_toggle_all_toggled(checked: bool):
            for band_layout in self.band_layouts:
                band_layout['toggle'].setChecked(checked)

        self.toggle_all.toggled.connect(on_toggle_all_toggled)

        self.label = QLabel('table: {}'.format(name))
        self.label.setWordWrap(True)
        self.toggle_all_layout.addWidget(self.toggle_all)
        self.toggle_all_layout.addWidget(self.label)

        self.layout = QVBoxLayout()

        self.layout.addLayout(self.toggle_all_layout)

        for band_item in self.band_layouts:
            self.layout.addLayout(band_item['layout'])

        self.setLayout(self.layout)

        self.on_hover_fn = lambda: ()

        self.installEventFilter(self)
        self.setMouseTracking(True)

    def eventFilter(self, obj, event):
        if event.type() == QEvent.Enter:
            for band in self.bands:
                pen = band.pen()
                pen.setWidth(LegendItem.SELECTED_WIDTH)
                band.setPen(pen)
                band.setVisible(not band.isVisible())
                band.setVisible(not band.isVisible())
            return True
        elif event.type() == QEvent.Leave:
            for band in self.bands:
                pen = band.pen()
                pen.setWidth(LegendItem.NORMAL_WIDTH)
                band.setPen(pen)
                band.setVisible(not band.isVisible())
                band.setVisible(not band.isVisible())
            return True
        return False

    def set_on_hover(self, on_hover_fn):
        self.on_hover_fn = on_hover_fn


class BandLegend(QWidget):

    def __init__(self, chart: QChart):
        QWidget.__init__(self)
        self.scroll_area = QScrollArea()
        self.scroll_area.setLayout(QVBoxLayout())
        self.scroll_area.setWidgetResizable(True)
        self.widget = QWidget()
        self.scroll_area.setWidget(self.widget)
        self.widget.setLayout(QVBoxLayout())
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.chart = chart
        self.layout.addWidget(self.scroll_area)
        self.setMouseTracking(True)


    def add_item(self, bands, name):
        self.widget.layout().addWidget(LegendItem(bands, name, self.chart))

