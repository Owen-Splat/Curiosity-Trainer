from PySide6.QtCore import QThread, Signal, QObject
import ctypes, math, win32ui, win32process, win32api
from mem_edit import Process
import time


class CuriosityManager(QObject):
    POS_PTR = (0x0809CAF8, (0x0, 0x90, 0x218, 0x0, 0x20, 0x1A0, 0x200))
    POS_SCALE = 100
    VELOCITY_PTR = (0x080ACEB8, (0xA0, 0x10, 0x0, 0xB0, 0x90, 0x320, 0xC8))


    def __init__(self, parent=None) -> None:
        QObject.__init__(self, parent)
        hwnd = win32ui.FindWindow("UnrealWindow", "Curiosity  ").GetSafeHwnd()
        self.PID = win32process.GetWindowThreadProcessId(hwnd)[1]
        process = win32api.OpenProcess(0x1F0FFF, True, self.PID)
        modules = win32process.EnumProcessModules(process)
        process.close()
        self.BASE_ADDRESS = modules[0]
        self.game = Process(self.PID)
        self.flyhack_thread = None
        self.speedwatch_thread = None


    def kill(self) -> None:
        """Kills any currently running threads so that the window can close without issue"""
        if self.flyhack_thread != None:
            self.flyhack_thread.on = False
        if self.speedwatch_thread != None:
            self.speedwatch_thread.on = False
        time.sleep(0.1)
        self.game.close()


    def isFocused(self) -> bool:
        """Checks if the game has focus. This is so that the hotkeys only trigger during gameplay"""
        hwnd = win32ui.GetForegroundWindow().GetSafeHwnd()
        return self.PID == win32process.GetWindowThreadProcessId(hwnd)[1]


    def isStillConnected(self) -> bool:
        """Checks if the game is still running by checking if its PID is in the list of running process IDs"""
        return self.PID in self.game.list_available_pids()


    def getPTRAddr(self, pointer: tuple) -> int:
        """Gets the final address of a pointer"""
        addr, offsets = pointer
        offset = self.BASE_ADDRESS + addr
        for i in range(len(offsets)):
            offset = self.game.read_memory(offset, ctypes.c_void_p()).value
            offset += offsets[i]
        return offset


    def readPosition(self) -> tuple:
        """Returns a tuple of the current player position"""
        addr = self.getPTRAddr(self.POS_PTR)
        pos = self.game.read_memory(addr - 0x10, Vector3())
        return (pos.X / self.POS_SCALE, pos.Y / self.POS_SCALE, pos.Z / self.POS_SCALE)


    def writePosition(self, _pos: tuple) -> None:
        """Writes the position to memory to teleport the player"""
        addr = self.getPTRAddr(self.POS_PTR)

        # set position
        pos = Vector3(
            _pos[0] * self.POS_SCALE,
            _pos[1] * self.POS_SCALE,
            _pos[2] * self.POS_SCALE
        )
        self.game.write_memory(addr - 0x10, pos)
        self.game.write_memory(addr - 0xD8, pos)

        # reset velocity
        addr = self.getPTRAddr(self.VELOCITY_PTR)
        self.game.write_memory(addr - 0x10, Vector3(0, 0, 0))


    # def toggleDoubleJump(self, on: bool) -> None:
    #     jump_addr = self.getPTRAddr(self.MAX_JUMPS_PTR)
    #     jump_num = 2 if on else 1
    #     effect_addr = self.getPTRAddr(self.JUMP_EFFECT_PTR)

    #     self.game.write_memory(jump_addr, ctypes.c_int32(jump_num))
    #     self.game.write_memory(effect_addr + 0x2, ctypes.c_bool(on))


    def toggleFlyHack(self, on: bool) -> None:
        if not on:
            if self.flyhack_thread != None:
                self.flyhack_thread.on = False
                addr = self.getPTRAddr(self.VELOCITY_PTR)
                self.game.write_memory(addr, ctypes.c_double(0.0)) # only reset z velocity when exiting flyhack
            return
        else:
            self.flyhack_thread = FlyHack(self.game, self.getPTRAddr(self.VELOCITY_PTR))
            self.flyhack_thread.start()
            return


    def toggleSpeedMonitor(self, on: bool) -> None:
        if not on:
            if self.speedwatch_thread != None:
                self.speedwatch_thread.on = False
            return
        else:
            self.speedwatch_thread = SpeedWatch(self.game, self.getPTRAddr(self.VELOCITY_PTR))
            self.speedwatch_thread.speed_emitter.connect(self.parent().getSpeed)
            self.speedwatch_thread.start()


class FlyHack(QThread):
    def __init__(self, _game: Process, _addr: int) -> None:
        QThread.__init__(self, None)
        self.game = _game
        self.addr = _addr
        self.on = True

    def run(self) -> None:
        while self.on:
            self.game.write_memory(self.addr, ctypes.c_double(325*10)) # high jump velocity x10
            time.sleep(1/60)


class SpeedWatch(QThread):
    speed_emitter = Signal(float)

    def __init__(self, _game: Process, _addr: int) -> None:
        QThread.__init__(self, None)
        self.game = _game
        self.addr = _addr
        self.on = True

    def run(self) -> None:
        while self.on:
            vel = self.game.read_memory(self.addr - 0x10, Vector3())
            speed = math.sqrt(pow(vel.X, 2) + pow(vel.Y, 2)) # we do not care about speed along the Z axis
            self.speed_emitter.emit(speed / 10)
            time.sleep(1/60)


class Vector3(ctypes.Structure):
    _fields_ = [
        ("X", ctypes.c_double),
        ("Y", ctypes.c_double),
        ("Z", ctypes.c_double)
    ]
