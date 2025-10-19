import ctypes, math, win32ui, win32process, win32api
from mem_edit import Process
import time


class CuriosityManager:
    PID = 0
    BASE_ADDRESS = 0x00000000
    LIFE_PTR = (0x080A8F50, (0x30, 0xB0, 0x70, 0x830, 0x48, 0x0, 0x44)) # might also not be static, I had gotten it down to 12 pointers and chosen the first one
    POS_PTR = (0x07F28FF0, (0xD30, 0x0, 0xBC0, 0x310, 0x198, 0xB0, 0x200))
    # POS_PTR = (0x080868A0, (0x30, 0x190, 0x10, 0x218, 0x430, 0xB0, 0x204)) # TODO: THIS POINTER IS NOT FULLY STATIC
    POS_SCALE = 100


    def __init__(self) -> None:
        process_all_access = 0x1F0FFF
        hwnd = win32ui.FindWindow("UnrealWindow", "Curiosity  ").GetSafeHwnd()
        self.PID = win32process.GetWindowThreadProcessId(hwnd)[1]
        process = win32api.OpenProcess(process_all_access, True, self.PID)
        modules = win32process.EnumProcessModules(process)
        self.BASE_ADDRESS = modules[0]
        process.close()
        self.game = Process(self.PID)


    def isFocused(self) -> bool:
        hwnd = win32ui.GetForegroundWindow().GetSafeHwnd()
        return self.PID == win32process.GetWindowThreadProcessId(hwnd)[1]


    def isStillConnected(self) -> bool:
        try:
            self.game.read_memory(0x0, ctypes.c_byte())
        except:
            return False
        else:
            return True


    def getPTRAddr(self, pointer: tuple) -> int:
        addr, offsets = pointer
        offset = self.BASE_ADDRESS + addr
        for i in range(len(offsets)):
            offset = self.game.read_memory(offset, ctypes.c_void_p()).value
            offset += offsets[i]
        return offset


    def readPosition(self) -> tuple:
        addr = self.getPTRAddr(self.POS_PTR)
        pos = self.game.read_memory(addr - 0x10, Vector3())
        return (pos.X / self.POS_SCALE, pos.Y / self.POS_SCALE, pos.Z / self.POS_SCALE)


    def writePosition(self, _pos: tuple) -> None:
        addr = self.getPTRAddr(self.POS_PTR)

        # set position
        pos = Vector3(
            _pos[0] * self.POS_SCALE,
            _pos[1] * self.POS_SCALE,
            _pos[2] * self.POS_SCALE
        )
        self.game.write_memory(addr - 0x10, pos)

        # # reset angle - NOT WORKING
        # self.game.write_memory(addr - 0x30, Vector3(0, 0, 0))

        # # reset velocity - NOT WORKING
        # self.game.write_memory(addr - 0x90, Vector3(0, 0, 0))


class SaveData(ctypes.Structure):
    _fields_ = [
        ("TimesSlept", ctypes.c_int32),
        ("SleepsRemaining", ctypes.c_int32), # LIFE_PTR result
        ("TimesMadeBed", ctypes.c_int32),
        ("BedsRemaining", ctypes.c_int32),
        ("PlayedIntro", ctypes.c_bool),
        ("UnlockedSleeping", ctypes.c_bool),
        ("ZonesEntered", ctypes.c_int32),
        ("ZonesFellFrom", ctypes.c_int32),
        ("NonCafeZonesEntered", ctypes.c_int32),
        ("WakeUpId", ctypes.c_int32)
    ]
    # BED_OBJECT_PATH = ""
    # BED_OBJECT_OFFSET = None # Vector
    # BED_OBJECT_ROTATION = 0.0 # Double
    # BED_ZONE_INDEX = 0
    # TRIGGERED_DIALOGUE_AUDIO_TRIGGERS = None # set property, int, maybe a bitmask?
    # TIMES_SPAWNED = 0


class Vector3(ctypes.Structure):
    _fields_ = [
        ("X", ctypes.c_double),
        ("Y", ctypes.c_double),
        ("Z", ctypes.c_double)
    ]