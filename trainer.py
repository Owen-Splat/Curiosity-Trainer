#!/usr/bin/env python3

from PySide6.QtCore import QTimer
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication
import main_window as window
import sys, os

# allow keyboard interrupts
def interruptHandler(sig, frame):
    sys.exit(0)
import signal
signal.signal(signal.SIGINT, interruptHandler)

# check if running from source
if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
    from sys import _MEIPASS
    IS_RUNNING_FROM_SOURCE = False
    ROOT_PATH = _MEIPASS
else:
    IS_RUNNING_FROM_SOURCE = True
    ROOT_PATH = os.path.dirname(os.path.realpath(__file__))

# set app id so the custom taskbar icon will show while running from source
if IS_RUNNING_FROM_SOURCE:
    try:
        from ctypes import windll
        windll.shell32.SetCurrentProcessExplicitAppUserModelID("Curiosity_Trainer")
    except AttributeError:
        pass # ignore for versions of windows before 7
    except ImportError:
        if sys.platform != "linux": raise

build_icon = "icon.ico"
if sys.platform == "darwin": # mac
    build_icon = "icon.icns"

app = QApplication([])
app.setStyle("cleanlooks")
app.setWindowIcon(QIcon(os.path.join(ROOT_PATH, "assets", build_icon)))

m = window.MainWindow()

# for keyboard interrupts
timer = QTimer()
timer.start(100)
timer.timeout.connect(lambda: None)

sys.exit(app.exec())
