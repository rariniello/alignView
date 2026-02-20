import numpy as np
import pyqtgraph as pg
import scipy.optimize as opt
from PyQt6 import QtCore, QtGui
from PyQt6.QtCore import QThread, pyqtSignal, pyqtSlot
from PyQt6.QtWidgets import QFileDialog, QMainWindow, QMessageBox

import analysis.image as an
import config
import gui.ui.ui_LineoutWindow as ui_LineoutWindow
from backends import camera_basler, camera_test, enumerate_basler, enumerate_test
from gui.worker import Worker


class AlignViewLineoutWindow(QMainWindow, ui_LineoutWindow.Ui_LineoutView):
    """Class that handles the main window and the gui functionality.

    The camera data source operates in a different thread from th gui.
    """

    def __init__(self, parent=None, icon=None):
        super().__init__(parent)

        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_DeleteOnClose, True)

        self.setupUi(self)
        self.connect_signal_slots()
        self.setup_plot()
        self.setup_xplot()
        self.setup_yplot()

    def connect_signal_slots(self):
        pass

    def setup_plot(self):
        self.plot = pg.PlotWidget()
        self.plot.invertY(True)
        self.plot.getViewBox().setDefaultPadding(0)
        self.imageViewLayout.addWidget(self.plot)
        self.imageItem = pg.ImageItem()
        self.plot.addItem(self.imageItem)
        cm = pg.colormap.get("magma")
        bar = pg.ColorBarItem(values=(0, 20_000), colorMap=cm, interactive=False)
        # bar.setImageItem(self.imageItem, insert_in=self.plot.getPlotItem())
        bar.setImageItem(self.imageItem)

    def setup_xplot(self):
        self.xplot = pg.PlotWidget()
        self.xLineoutLayout.addWidget(self.xplot)
        self.xPlotItem = self.xplot.plot()
        pen = pg.mkPen(color="r")
        self.xFitItem = self.xplot.plot(pen=pen)
        self.xplot.setXLink(self.plot)

    def setup_yplot(self):
        self.yplot = pg.PlotWidget()
        self.yplot.invertY(True)
        self.yLineoutLayout.addWidget(self.yplot)
        self.yPlotItem = self.yplot.plot()
        pen = pg.mkPen(color="r")
        self.yFitItem = self.yplot.plot(pen=pen)
        self.yplot.setYLink(self.plot)

    @pyqtSlot(dict)
    def on_new_image(self, data):
        self.update_xplot(data)
        self.update_yplot(data)
        self.update_plot(data)

    def update_xplot(self, data):
        # Plot the raw data
        index = int((data["centroid"][1] - data["sy"]) / data["scaley"])
        coord = data["x"]
        lineout = data["image"][index, :]
        self.xPlotItem.setData(coord, lineout)
        # Fit the curve
        px = self.fit_gaussian(coord, lineout, data["centroid"][0])
        self.xFitItem.setData(coord, an.gaussian(coord, *px))
        value = self.scale_number_units(px[2] * self.pixelCalField.value() * 1e-6, "m")
        self.sigmaXLabel.setText("Sigma X: " + value)

    def update_yplot(self, data):
        # Plot the raw data
        index = int((data["centroid"][0] - data["sx"]) / data["scalex"])
        coord = data["y"]
        lineout = data["image"][:, index]
        self.yPlotItem.setData(lineout, coord)
        # Fit the curve
        py = self.fit_gaussian(coord, lineout, data["centroid"][1])
        self.yFitItem.setData(an.gaussian(coord, *py), coord)
        value = self.scale_number_units(py[2] * self.pixelCalField.value() * 1e-6, "m")
        self.sigmaYLabel.setText("Sigma Y: " + value)

    def update_plot(self, data):
        img = data["image"]
        self.imageItem.setImage(img, autoLevels=True)
        tr = QtGui.QTransform()
        tr.translate(data["sx"] * data["scalex"], data["sy"] * data["scaley"])
        tr.scale(data["scalex"], data["scaley"])
        self.imageItem.setTransform(tr)

    def fit_gaussian(self, x, y, x0):
        # A, x0, C, offset
        A0 = np.max(y)
        C0 = 0.001
        y0 = y[0]
        bounds = ([0.0, x[0], 0.0, 0.0], [np.inf, x[-1], np.inf, np.inf])
        try:
            p, covariancex = opt.curve_fit(
                an._gaussian, x, y, p0=(A0, x0, C0, y0), bounds=bounds
            )
            p[2] = 1 / np.sqrt(2 * p[2])
        except RuntimeError:
            p = None
        return p

    def scale_number_units(self, value, unit, precision=4):
        prefixs = np.array(["T", "G", "M", "k", "", "m", "μ", "n", "p", "f"])
        scales = 0.9 * np.array(
            [1.0e12, 1.0e9, 1.0e6, 1.0e3, 1.0, 1.0e-3, 1.0e-6, 1.0e-9, 1.0e-12, 1.0e-15]
        )
        sel = np.array(value / scales, dtype="int") > 0
        if sum(sel) > 0:
            prefix = prefixs[sel][0]
            scale = scales[sel][0]
        else:
            scale = 1
            prefix = ""
        value = value / scale
        return f"{value:#.{precision}g}{prefix}{unit}"
