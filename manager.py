import ctypes, win32ui, win32process, win32api
from mem_edit import Process


class CuriosityManager:
    BASE_ADDRESS = 0x00000000
    LIFE_PTR = (0x080A8F50, (0x30, 0xB0, 0x70, 0x830, 0x48, 0x0, 0x44))
    POS_PTR = (0x080868A0, (0x30, 0x190, 0x10, 0x218, 0x430, 0xB0, 0x204))


    def __init__(self) -> None:
        process_all_access = 0x1F0FFF
        hwnd = win32ui.FindWindow("UnrealWindow", "Curiosity  ").GetSafeHwnd()
        pid = win32process.GetWindowThreadProcessId(hwnd)[1]
        process = win32api.OpenProcess(process_all_access, True, pid)
        modules = win32process.EnumProcessModules(process)
        self.BASE_ADDRESS = modules[0]
        process.close()
        self.game = Process(pid)


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


    def readPosition(self) -> list:
        addr = self.getPTRAddr(self.POS_PTR)
        z = self.game.read_memory(addr, ctypes.c_float()) * 100
        y = self.game.read_memory(addr - 8, ctypes.c_float()) * 100
        x = self.game.read_memory(addr - 16, ctypes.c_float()) * 100
        return [x.value, y.value, z.value]


    def writePosition(self, pos: list) -> None:
        addr = self.getPTRAddr(self.POS_PTR)
        self.game.write_memory(addr, ctypes.c_float(pos[2] / 100))
        self.game.write_memory(addr - 8, ctypes.c_float(pos[1] / 100))
        self.game.write_memory(addr - 16, ctypes.c_float(pos[0] / 100))
