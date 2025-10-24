from PySide6.QtCore import Qt
from PySide6.QtGui import QDoubleValidator
from PySide6.QtWidgets import (QMainWindow, QWidget, QLabel, QLineEdit, QListWidget, QPushButton, QGroupBox,
                               QHBoxLayout, QVBoxLayout, QMessageBox)
from data import DEFAULT_POSITIONS, POSITION_FILE_PATH, SAVED_POSITIONS, VERSION
from manager import CuriosityManager
from global_hotkeys import register_hotkey, start_checking_hotkeys, stop_checking_hotkeys
import json


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super(MainWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.show()
        self.setMinimumSize(686, 402)

        self.manager = None

        self.positions = SAVED_POSITIONS if SAVED_POSITIONS else DEFAULT_POSITIONS
        pos_list: QListWidget = self.ui.findWidget("PositionList", QListWidget)
        pos_list.addItems(list(self.positions.keys()))
        pos_list.setCurrentRow(0)

        register_hotkey("b", self.savePosHotkey, None)
        register_hotkey("t", self.loadPosHotkey, None)
        # register_hotkey("j", self.doubleJumpHotkey, None) // hotkey isn't too necessary
        register_hotkey("h", self.flyHackHotkey, None)
        start_checking_hotkeys()


    def closeEvent(self, event):
        """Save the position list before closing"""

        stop_checking_hotkeys()
        if self.manager != None:
            self.manager.kill()
        with open(POSITION_FILE_PATH, 'w') as f:
            f.write(json.dumps(self.positions, indent=4))
        return super().closeEvent(event)


    def connect(self, show_error=True) -> bool:
        """Checks if the app can access the game memory"""

        try:
            if self.manager == None:
                self.manager = CuriosityManager(self)
            if not self.manager.isStillConnected():
                self.manager = None
                raise ConnectionError
        except:
            if show_error:
                self.ui.showError("The game must be running first!")
            return False
        else:
            return True


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

        if not self.connect(show_error=False):
            return
        if not self.manager.isFocused():
            return

        self.updatePos()
        self.ui.findWidget("NameField", QLineEdit).setText("Hotkey")
        self.savePos()


    def loadPos(self) -> None:
        """Teleports to the selected position"""

        if not self.connect():
            return

        pos_list: QListWidget = self.ui.findWidget("PositionList", QListWidget)
        if pos_list.count() == 0:
            return

        self.manager.writePosition(self.positions[pos_list.item(pos_list.currentRow()).text()])


    def loadPosHotkey(self) -> None:
        """Teleports to the selected position when the hotkey is pressed with the game focused"""

        if not self.connect(show_error=False):
            return
        if not self.manager.isFocused():
            return

        self.loadPos()


    def deletePos(self) -> None:
        """Deletes a position from the list"""

        pos_list: QListWidget = self.ui.findWidget("PositionList", QListWidget)
        current_item = pos_list.currentItem()
        if current_item == None:
            return

        pos_list.takeItem(pos_list.currentRow())
        del self.positions[current_item.text()]


    # def toggleDoubleJump(self) -> None:
    #     """Toggles the double jump ability"""

    #     if not self.connect():
    #         return

    #     jump_button: QPushButton = self.ui.findWidget("JumpButton", QPushButton)
    #     state = jump_button.isChecked()
    #     if state:
    #         jump_button.setText("Disable Double Jump")
    #     else:
    #         jump_button.setText("Enable Double Jump")
    #     self.manager.toggleDoubleJump(state)


    # def doubleJumpHotkey(self) -> None:
    #     """Toggles the double jump ability when the hotkey is pressed"""

    #     if not self.connect(show_error=False):
    #         return
    #     if not self.manager.isFocused():
    #         return

    #     jump_button: QPushButton = self.ui.findWidget("JumpButton", QPushButton)
    #     jump_button.setChecked(not jump_button.isChecked())
    #     self.toggleDoubleJump()


    def toggleFlyHack(self) -> None:
        """Activates a fly hack"""

        if not self.connect():
            return

        fly_button: QPushButton = self.ui.findWidget("FlyButton", QPushButton)
        state = fly_button.isChecked()
        if state:
            fly_button.setText("Disable Fly Hack")
        else:
            fly_button.setText("Enable Fly Hack")
        self.manager.toggleFlyHack(state)


    def flyHackHotkey(self) -> None:
        """Activates fly hack when the hotkey is pressed"""

        if not self.connect(show_error=False):
            return
        if not self.manager.isFocused():
            return

        fly_button: QPushButton = self.ui.findWidget("FlyButton", QPushButton)
        fly_button.setChecked(not fly_button.isChecked())
        self.toggleFlyHack()


    def toggleSpeedMonitor(self) -> None:
        """Outputs the current player speed"""

        if not self.connect():
            return

        speed_button: QPushButton = self.ui.findWidget("SpeedButton", QPushButton)
        state = speed_button.isChecked()
        if state:
            speed_button.setText("Stop")
        else:
            speed_button.setText("Monitor Speed")
            self.getSpeed(0.0)
        self.manager.toggleSpeedMonitor(state)


    def getSpeed(self, speed: float) -> None:
        speed_field: QLineEdit = self.ui.findWidget("SpeedField", QLineEdit)
        speed_field.setText(f"{speed:.3f}")


### UI CODE <-------------------------------------------------------------------------------------
class Ui_MainWindow(object):
    def setupUi(self, window: QMainWindow) -> None:
        self.window = window
        window.setWindowTitle(f"Curiosity Trainer v{VERSION}")

        central_widget = QWidget(window)
        main_layout = QVBoxLayout(central_widget)

        main_layout.addWidget(self.createPositionGroup(), 5)
        main_layout.addWidget(self.createMiscGroup(), 2)

        central_widget.setLayout(main_layout)
        window.setCentralWidget(central_widget)


    def createPositionGroup(self) -> QWidget:
        group = QGroupBox("Position Editor", self.window.centralWidget())
        group.setStyleSheet(r"QGroupBox {font-size: 20px; margin-top: 20px;} QGroupBox::title {subcontrol-position: top; padding: 0px 5px 0px 5px;}")
        group_layout = QHBoxLayout()

        # left side
        left_layout = QVBoxLayout()
        pos_list = QListWidget(group)
        pos_list.setObjectName("PositionList")
        left_layout.addWidget(pos_list)
        left_hl_layout = QHBoxLayout()
        del_button = QPushButton("Delete Position", group)
        del_button.clicked.connect(self.window.deletePos)
        left_hl_layout.addWidget(del_button, 1)
        tel_button = QPushButton("Teleport To Position", group)
        tel_button.clicked.connect(self.window.loadPos)
        left_hl_layout.addWidget(tel_button, 1)
        left_layout.addLayout(left_hl_layout)
        group_layout.addLayout(left_layout)

        # right side
        right_layout = QVBoxLayout()
        validator = QDoubleValidator(-9999.999, 9999.999, 3, group)
        validator.setNotation(QDoubleValidator.Notation.StandardNotation)
        field_layout = QHBoxLayout()
        x_pos = QLineEdit("0.0", group)
        x_pos.setObjectName("XPosField")
        x_pos.setValidator(validator)
        field_layout.addWidget(x_pos)
        y_pos = QLineEdit("0.0", group)
        y_pos.setObjectName("YPosField")
        y_pos.setValidator(validator)
        field_layout.addWidget(y_pos)
        z_pos = QLineEdit("0.0", group)
        z_pos.setObjectName("ZPosField")
        z_pos.setValidator(validator)
        field_layout.addWidget(z_pos)
        right_layout.addLayout(field_layout)
        update_button = QPushButton("Update Position", group)
        update_button.clicked.connect(self.window.updatePos)
        right_layout.addWidget(update_button)
        edit_layout = QHBoxLayout()
        name_edit = QLineEdit(group)
        name_edit.setObjectName("NameField")
        name_edit.setPlaceholderText("Enter Position Name")
        edit_layout.addWidget(name_edit, 2)
        save_button = QPushButton("Save Position", group)
        save_button.clicked.connect(self.window.savePos)
        edit_layout.addWidget(save_button, 1)
        right_layout.addLayout(edit_layout)
        group_layout.addLayout(right_layout)

        group.setLayout(group_layout)
        return group


    def createMiscGroup(self) -> QWidget:
        group = QGroupBox("Miscellaneous", self.window.centralWidget())
        group.setStyleSheet(r"QGroupBox {font-size: 20px; margin-top: 20px;} QGroupBox::title {subcontrol-position: top; padding: 0px 5px 0px 5px;}")
        group_layout = QVBoxLayout()

        buttons_layout = QHBoxLayout()
        # jump_button = QPushButton("Enable Double Jump", group)
        # jump_button.setObjectName("JumpButton")
        # jump_button.setCheckable(True)
        # jump_button.clicked.connect(self.window.toggleDoubleJump)
        # buttons_layout.addWidget(jump_button)
        fly_button = QPushButton("Enable Fly Hack", group)
        fly_button.setObjectName("FlyButton")
        fly_button.setCheckable(True)
        fly_button.clicked.connect(self.window.toggleFlyHack)
        buttons_layout.addWidget(fly_button)
        group_layout.addLayout(buttons_layout)

        speed_layout = QHBoxLayout()
        speed_field_layout = QHBoxLayout()
        speed_field_layout.addWidget(QLabel("Current Speed"))
        speed_view = QLineEdit("0.0", group)
        speed_view.setObjectName("SpeedField")
        speed_field_layout.addWidget(speed_view)
        speed_layout.addLayout(speed_field_layout, 1)
        speed_button = QPushButton("Monitor Speed", group)
        speed_button.setObjectName("SpeedButton")
        speed_button.setCheckable(True)
        speed_button.clicked.connect(self.window.toggleSpeedMonitor)
        speed_layout.addWidget(speed_button, 1)
        group_layout.addLayout(speed_layout)

        group.setLayout(group_layout)
        return group


    def findWidget(self, widget_name: str, widget_type) -> QWidget:
        return self.window.findChild(widget_type, widget_name, Qt.FindChildOption.FindChildrenRecursively)


    def showError(self, msg: str) -> None:
        box = QMessageBox(self.window)
        box.setWindowTitle("Error")
        box.setText(msg)
        box.exec()
