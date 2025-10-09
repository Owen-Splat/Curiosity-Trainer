from PySide6.QtWidgets import (QMainWindow, QWidget, QCheckBox, QComboBox, QSpinBox, QPushButton, QHBoxLayout, QVBoxLayout, QSizePolicy, QSpacerItem, QMessageBox)
from save import SaveData
from pathlib import Path
import sys


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super(MainWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.show()


    def readSave(self) -> bool:
        """Reads the user save file and stores it as an object"""

        home = Path.home()

        if sys.platform == "win32":
            home = home / "AppData/Local"
        elif sys.platform == "linux":
            home = home / ".local/share"
        elif sys.platform == "darwin":
            home = home / "Library/Application Support"

        self.save_dir = home / "Curiosity/Saved/SaveGames"

        if not self.save_dir.exists():
            return False

        with open(self.save_dir / "Run1.sav", "rb") as f:
            self.save_data = SaveData(f.read())

        return True


    def editSave(self) -> None:
        """Edits the save data. This can be done while the game is still open. The save data is read when the player selects Resume Game"""

        has_save = self.readSave() # read the save again so that old save data does not carry over (bed placements for example)

        if not has_save:
            self.ui.showError("User save data was not found")
            return

        settings = {}
        for c in self.centralWidget().children():
            match c:
                case QSpinBox():
                    settings[c.objectName()] = c.value()
                case QCheckBox():
                    settings[c.objectName()] = int(c.isChecked()) * 0x10 # this is saved as 0x10 when true, idk why
                case QComboBox():
                    settings[c.objectName()] = c.currentIndex()

        # write save data using the settings
        with open(self.save_dir / "Run1.sav", "wb") as f:
            f.write(self.save_data.save(settings))


class Ui_MainWindow(object):
    def setupUi(self, window: QMainWindow) -> None:
        self.window = window
        window.setWindowTitle("Curiosity Trainer")
        spacing = 175

        central_widget = QWidget(window)
        vl = QVBoxLayout(central_widget)

        hl = QHBoxLayout()
        beds_count = QSpinBox(central_widget)
        beds_count.setObjectName("Beds Remaining")
        beds_count.setPrefix("Beds:  ")
        beds_count.setMinimum(0)
        beds_count.setMaximum(999)
        beds_count.setValue(999)
        lives_count = QSpinBox(central_widget)
        lives_count.setObjectName("Sleeps Remaining")
        lives_count.setPrefix("Lives:  ")
        lives_count.setMinimum(0)
        lives_count.setMaximum(999)
        lives_count.setValue(999)
        sleep_check = QCheckBox("Can Sleep", central_widget)
        sleep_check.setObjectName("Unlocked Sleeping")
        sleep_check.setChecked(True)
        hl.addWidget(beds_count)
        hl.addSpacerItem(self.createHorizontalSpacer())
        hl.addWidget(lives_count)
        hl.addSpacerItem(self.createHorizontalSpacer())
        hl.addWidget(sleep_check)
        vl.addLayout(hl)

        hl = QHBoxLayout()
        respawn_box = QComboBox(central_widget)
        respawn_box.setObjectName("WakeUpId")
        respawn_box.addItems((
            "Spawn:  Forest",
            "Spawn:  City Cafe",
            "Spawn:  Pirate Cafe",
            "Spawn:  Catnip Cafe",
            "Spawn:  Music Cafe",
            "Spawn:  Laser Cafe",
            "Spawn:  Home Cafe",
            # "Spawn:  Home", # not needed
        ))
        edit_button = QPushButton("Edit", central_widget)
        edit_button.clicked.connect(window.editSave)
        hl.addWidget(respawn_box)
        hl.addSpacerItem(self.createHorizontalSpacer())
        hl.addWidget(edit_button)
        vl.addLayout(hl)

        central_widget.setLayout(vl)
        window.setCentralWidget(central_widget)

        for c in central_widget.findChildren(QCheckBox):
            c.setFixedWidth(spacing)
        for c in central_widget.findChildren(QComboBox):
            c.setFixedWidth(spacing)
        for c in central_widget.findChildren(QPushButton):
            c.setFixedWidth(spacing*2)
        for c in central_widget.findChildren(QSpinBox):
            c.setFixedWidth(spacing)


    def createHorizontalSpacer(self) -> QSpacerItem:
        return QSpacerItem(1, 30, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)


    def showError(self, msg: str) -> None:
        box = QMessageBox(self.window)
        box.setWindowTitle("Error")
        box.setText(msg)
        box.exec()
