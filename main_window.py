from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QMainWindow, QWidget, QLabel, QLineEdit, QListWidget, QPushButton,
                               QHBoxLayout, QVBoxLayout, QSizePolicy, QSpacerItem, QMessageBox)
from manager import CuriosityManager
from pathlib import Path
import sys


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super(MainWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.show()
        self.setMinimumSize(500, 250)
        self.manager = None
        self.saved_pos = (0.0, 0.0, 0.0)


    def connect(self) -> bool:
        try:
            if self.manager == None:
                self.manager = CuriosityManager()
        except:
            self.ui.showError("The game must be running first!")

        if self.manager.isStillConnected():
            return True
        else:
            self.ui.showError("Unable to fetch game data!")
            return False


    def savePos(self) -> None:
        if self.connect():
            self.saved_pos = self.manager.readPosition()


    def loadPos(self) -> None:
        if self.connect():
            self.manager.writePosition(self.saved_pos)


class Ui_MainWindow(object):
    def setupUi(self, window: QMainWindow) -> None:
        self.window = window
        window.setWindowTitle("Curiosity Trainer")
        spacing = 175

        central_widget = QWidget(window)
        main_layout = QHBoxLayout(central_widget)

        # left side
        left_layout = QVBoxLayout()
        pos_list = QListWidget(central_widget)
        left_layout.addWidget(pos_list)
        tel_button = QPushButton("Teleport To Position", central_widget)
        left_layout.addWidget(tel_button)
        main_layout.addLayout(left_layout)

        # right side
        right_layout = QVBoxLayout()

        x_layout = QHBoxLayout()
        x_text = QLabel("X", central_widget)
        x_pos = QLineEdit("0.0", central_widget)
        x_pos.setReadOnly(True)
        x_layout.addWidget(x_text)
        x_layout.addWidget(x_pos)
        right_layout.addLayout(x_layout)

        y_layout = QHBoxLayout()
        y_text = QLabel("Y", central_widget)
        y_pos = QLineEdit("0.0", central_widget)
        y_pos.setReadOnly(True)
        y_layout.addWidget(y_text)
        y_layout.addWidget(y_pos)
        right_layout.addLayout(y_layout)

        z_layout = QHBoxLayout()
        z_text = QLabel("Z", central_widget)
        z_pos = QLineEdit("0.0", central_widget)
        z_pos.setReadOnly(True)
        z_layout.addWidget(z_text)
        z_layout.addWidget(z_pos)
        right_layout.addLayout(z_layout)

        update_button = QPushButton("Update Position", central_widget)
        right_layout.addWidget(update_button)

        edit_layout = QHBoxLayout()
        name_edit = QLineEdit(central_widget)
        name_edit.setPlaceholderText("Enter Position Name")
        edit_layout.addWidget(name_edit)
        save_button = QPushButton("Save Position", central_widget)
        edit_layout.addWidget(save_button)
        right_layout.addLayout(edit_layout)
        main_layout.addLayout(right_layout)

        central_widget.setLayout(main_layout)
        window.setCentralWidget(central_widget)


    def createHorizontalSpacer(self) -> QSpacerItem:
        return QSpacerItem(1, 30, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)


    def showError(self, msg: str) -> None:
        box = QMessageBox(self.window)
        box.setWindowTitle("Error")
        box.setText(msg)
        box.exec()
