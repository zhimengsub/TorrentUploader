from PyQt5.QtGui import QIcon
from addict import Dict

from utils.const import PATHS

ICONS = Dict()


def init_icons():
    ICONS.MAIN = QIcon(str(PATHS.ICON))
    ICONS.PUBMORE = QIcon(str(PATHS.SRC.PUBMORE))
    ICONS.PUBDIRECT = QIcon(str(PATHS.SRC.PUBDIRECT))
    ICONS.MAKEBT = QIcon(str(PATHS.SRC.MAKEBT))
    ICONS.MOVETO = QIcon(str(PATHS.SRC.MOVETO))
    ICONS.OPEN = QIcon(str(PATHS.SRC.OPEN))

