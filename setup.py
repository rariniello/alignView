import sys
import os
from PyQt6 import uic


def map(uiDirName, uiModName):
    return os.path.join('gui', 'ui'), "ui_"+uiModName


def build_ui():
    uic.compileUiDir('designer', map=map)


if __name__ == '__main__':


    build_ui()
    sys.exit()