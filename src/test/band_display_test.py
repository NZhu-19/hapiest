import math
import random
import threading
from time import sleep

from PyQt5 import QtWidgets

from data_structures.bands import Band, Bands
from test.test import Test
from widgets.graphing.band_display_window_gui import BandDisplayWindowGui


class BandDisplayTest(Test):

    def __init__(self):
        Test.__init__(self)

    def name(self) -> str:
        return 'band display test'

    def test(self) -> bool:
        app = QtWidgets.QApplication([])
        window = QtWidgets.QMainWindow()
        widget = BandDisplayWindowGui(0)

        def close_window():
            sleep(0.25)
            widget.close()
            window.deleteLater()

        step = 0.1

        x = list(map(lambda x: float(x) * step, range(0, int(100.0 / step))))

        def random_band():
            freq = float(random.randint(1, 10)) / 100
            amp = float(random.randint(1, 100))
            y = [0.0] * len(x)
            for i in range(0, int(100.0 / step)):
                y[i] = abs(amp * math.sin(freq * x[i]))
            return Band(x, y, f'{freq}, {amp}')

        bands1 = Bands([], 'of')
        for i in range(0, 10):
            bands1.add_band(random_band())
        bands2 = Bands([], 'aw')
        for i in range(0, 10):
            bands2.add_band(random_band())

        t = threading.Thread(target=close_window)
        t.start()
        widget.setMinimumSize(256, 256)
        widget.add_bands(bands1)
        widget.add_bands(bands2)
        window.setCentralWidget(widget)
        window.show()
        return app.exec_() == 0
