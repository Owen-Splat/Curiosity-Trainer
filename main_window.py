from PySide6.QtCore import Qt, QRegularExpression, QEvent
from PySide6.QtGui import QRegularExpressionValidator, QKeyEvent
from PySide6.QtWidgets import (QMainWindow, QWidget, QLabel, QLineEdit, QListWidget, QPushButton,
                               QHBoxLayout, QVBoxLayout, QSizePolicy, QSpacerItem, QMessageBox)
from manager import CuriosityManager
from pathlib import Path
from global_hotkeys import register_hotkey, start_checking_hotkeys, stop_checking_hotkeys


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super(MainWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.show()
        self.setMinimumSize(500, 250)
        self.manager = None
        self.positions = {
            'Ascent': (-260.872, 228.578, 299.838),
            'Aquarium': (275.933, 278.339, 327.438),
            'Trip': (277.042, -289.551, 360.177),
            'Hands': (295.013, -265.721, 380.029),
            'Coffin Skip': (235.135, -317.513, 388.809),
            'Amphitheater': (314.005, 336.79, 396.428),
            'Lasers': (-277.931, -255.663, 422.543),
        }
        pos_list: QListWidget = self.ui.findWidget("PositionList", QListWidget)
        pos_list.addItems(list(self.positions.keys()))
        pos_list.setCurrentRow(0)

        register_hotkey("p", None, self.savePosHotkey, False)
        register_hotkey("t", None, self.loadPos, False)
        start_checking_hotkeys()


    def connect(self) -> bool:
        """Checks if the app can access the game memory"""

        try:
            if self.manager == None:
                self.manager = CuriosityManager()
        except:
            self.ui.showError("The game must be running first!")
            return False

        if self.manager.isStillConnected():
            return True
        else:
            self.ui.showError("Unable to fetch game data!")
            return False


    def updatePos(self) -> None:
        """Reads game memory to display the current player coordinates"""

        if not self.connect():
            return

        pos = self.manager.readPosition()
        self.ui.findWidget("XPosField", QLineEdit).setText(f"{pos[0]:.3f}")
        self.ui.findWidget("YPosField", QLineEdit).setText(f"{pos[1]:.3f}")
        self.ui.findWidget("ZPosField", QLineEdit).setText(f"{pos[2]:.3f}")


    def savePos(self) -> None:
        """Adds the current position to the list"""

        if not self.connect():
            return

        name: str = self.ui.findWidget("NameField", QLineEdit).text()
        if len(name.strip()) == 0:
            self.ui.showError("Name must not be empty!")
            return

        pos_list: QListWidget = self.ui.findWidget("PositionList", QListWidget)
        existing_items = pos_list.findItems(name, Qt.MatchFlag.MatchExactly)
        if len(existing_items) == 0:
            pos_list.addItem(name)
            pos_list.setCurrentRow(pos_list.count() - 1)
        else:
            pos_list.setCurrentRow(pos_list.row(existing_items[0]))

        x = float(self.ui.findWidget("XPosField", QLineEdit).text())
        y = float(self.ui.findWidget("YPosField", QLineEdit).text())
        z = float(self.ui.findWidget("ZPosField", QLineEdit).text())
        self.positions[name] = (x, y, z)


    def savePosHotkey(self) -> None:
        """Updates the current position then saves it when the hotkey is released"""

        self.updatePos()
        self.ui.findWidget("NameField", QLineEdit).setText("Hotkey")
        self.savePos()
        self.loadPos()


    def loadPos(self) -> None:
        """Teleports to the selected position"""

        if not self.connect():
            return

        pos_list: QListWidget = self.ui.findWidget("PositionList", QListWidget)
        if pos_list.count() == 0:
            return

        self.manager.writePosition(self.positions[pos_list.item(pos_list.currentRow()).text()])


    def closeEvent(self, event):
        print(self.positions)
        stop_checking_hotkeys()
        return super().closeEvent(event)


    def eventFilter(self, watched, event):
        if event.type() == QEvent.Type.KeyPress:
            key_event = QKeyEvent(event)
            match key_event.key:
                case Qt.Key.Key_F:
                    self.updatePos()
                    self.ui.findWidget("NameField", QLineEdit).setText("Hotkey")
                    self.savePos()
                case Qt.Key.Key_T:
                    self.loadPos()

        return super().eventFilter(watched, event)


class Ui_MainWindow(object):
    def setupUi(self, window: QMainWindow) -> None:
        self.window = window
        window.setWindowTitle("Curiosity Trainer")

        central_widget = QWidget(window)
        main_layout = QHBoxLayout(central_widget)

        # left side
        left_layout = QVBoxLayout()
        pos_list = QListWidget(central_widget)
        pos_list.setObjectName("PositionList")
        left_layout.addWidget(pos_list)
        tel_button = QPushButton("Teleport To Position", central_widget)
        tel_button.clicked.connect(window.loadPos)
        tel_button.setShortcut("T")
        left_layout.addWidget(tel_button)
        main_layout.addLayout(left_layout)

        # right side
        right_layout = QVBoxLayout()
        numbers = QRegularExpression(r"^[0-9]{1,3}(?:\.[0-9]{1,3})?$")
        validator = QRegularExpressionValidator(numbers)

        x_layout = QHBoxLayout()
        x_text = QLabel("X", central_widget)
        x_pos = QLineEdit("0.0", central_widget)
        x_pos.setObjectName("XPosField")
        x_pos.setValidator(validator)
        x_layout.addWidget(x_text)
        x_layout.addWidget(x_pos)
        right_layout.addLayout(x_layout)

        y_layout = QHBoxLayout()
        y_text = QLabel("Y", central_widget)
        y_pos = QLineEdit("0.0", central_widget)
        y_pos.setObjectName("YPosField")
        y_pos.setValidator(validator)
        y_layout.addWidget(y_text)
        y_layout.addWidget(y_pos)
        right_layout.addLayout(y_layout)

        z_layout = QHBoxLayout()
        z_text = QLabel("Z", central_widget)
        z_pos = QLineEdit("0.0", central_widget)
        z_pos.setObjectName("ZPosField")
        z_pos.setValidator(validator)
        z_layout.addWidget(z_text)
        z_layout.addWidget(z_pos)
        right_layout.addLayout(z_layout)

        update_button = QPushButton("Update Position", central_widget)
        update_button.clicked.connect(window.updatePos)
        right_layout.addWidget(update_button)

        edit_layout = QHBoxLayout()
        name_edit = QLineEdit(central_widget)
        name_edit.setObjectName("NameField")
        name_edit.setPlaceholderText("Enter Position Name")
        edit_layout.addWidget(name_edit)
        save_button = QPushButton("Save Position", central_widget)
        save_button.clicked.connect(window.savePos)
        edit_layout.addWidget(save_button)
        right_layout.addLayout(edit_layout)
        main_layout.addLayout(right_layout)

        central_widget.setLayout(main_layout)
        window.setCentralWidget(central_widget)


    def createHorizontalSpacer(self) -> QSpacerItem:
        return QSpacerItem(1, 30, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)


    def findWidget(self, widget_name: str, widget_type) -> QWidget:
        return self.window.findChild(widget_type, widget_name, Qt.FindChildOption.FindChildrenRecursively)


    def showError(self, msg: str) -> None:
        box = QMessageBox(self.window)
        box.setWindowTitle("Error")
        box.setText(msg)
        box.exec()
