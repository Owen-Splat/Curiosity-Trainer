import ctypes, win32ui, win32process, win32api
from mem_edit import Process


class CuriosityManager:
    PID = 0
    BASE_ADDRESS = 0x00000000
    LIFE_PTR = (0x080A8F50, (0x30, 0xB0, 0x70, 0x830, 0x48, 0x0, 0x44))
    POS_PTR = (0x080868A0, (0x30, 0x190, 0x10, 0x218, 0x430, 0xB0, 0x204)) # TODO: THIS POINTER IS NOT FULLY STATIC
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
        addr = self.getPTRAddr(self.POS_PTR) - 0x4
        z = self.game.read_memory(addr, ctypes.c_double())
        y = self.game.read_memory(addr - 8, ctypes.c_double())
        x = self.game.read_memory(addr - 16, ctypes.c_double())
        return (x.value / self.POS_SCALE, y.value / self.POS_SCALE, z.value / self.POS_SCALE)


    def writePosition(self, pos: tuple) -> None:
        addr = self.getPTRAddr(self.POS_PTR) - 0x4
        self.game.write_memory(addr, ctypes.c_double(pos[2] * self.POS_SCALE))
        self.game.write_memory(addr - 8, ctypes.c_double(pos[1] * self.POS_SCALE))
        self.game.write_memory(addr - 16, ctypes.c_double(pos[0] * self.POS_SCALE))


    def refillBedsLives(self) -> None:
        addr = self.getPTRAddr(self.LIFE_PTR)
        self.game.write_memory(addr, ctypes.c_int(999))
        self.game.write_memory(addr + 8, ctypes.c_int(999))
