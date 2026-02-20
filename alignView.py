import os
import sys

import config
import setup

if __name__ == "__main__":

    config.defPaths()
    # Compile designer files each time we run if we are in a development environment
    if not config.isFrozen():
        setup.build_ui()

    # We import in the if statement in case we ever want to check that
    # dependencies exist before we start importing

    from PyQt6 import QtCore
    from PyQt6.QtWidgets import QApplication

    # app and mainWin are defined globably in the application
    # best to avoid defining things here so we don't clutter the global namespace
    # XXX For pyqtgraph, not sure this does anything
    os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "1"
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        QtCore.Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )

    app = QApplication(sys.argv)

    if app.styleHints().colorScheme() == QtCore.Qt.ColorScheme.Dark:
        config.darkMode = True

    import pyqtgraph as pg

    # Set pyqtgraph defaults
    if config.darkMode:
        pg.setConfigOption("background", "#222222")
        pg.setConfigOption("foreground", "#a9a9a9")
    else:
        pg.setConfigOption("background", "w")
        pg.setConfigOption("foreground", "k")
    pg.setConfigOption("antialias", True)
    pg.setConfigOption("imageAxisOrder", "row-major")

    from gui import mainWindow

    mainWin = mainWindow.AlignViewMainWindow()

    mainWin.show()
    sys.exit(app.exec())
