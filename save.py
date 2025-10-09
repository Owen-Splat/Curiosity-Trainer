from io import BytesIO

def readInt(data: bytes, start: int, size: int, signed: bool = False) -> int:
    return int.from_bytes(data[start : start + size], "little", signed=signed)


class SaveData:
    def __init__(self, data: bytes) -> None:
        self.data = data
        self.start_address = data.find("/Game/Save/Saves/RunSave.RunSave_C".encode("ASCII")) + 0x24


    def save(self, settings: dict) -> bytes:
        """Outputs data in the Curiosity save format. Currently just edits preexisting data, does not add things not already in the save file"""
        with BytesIO() as f:
            f.write(self.data)
            for k,v in SAVE_SETTINGS.items():
                pos = self.data.find(k.encode("ASCII"))
                if pos == -1:
                    continue
                num_bytes = 4 if v.startswith("Int") else 1
                pos += len(k) + 1 + 4 + len(v) + 1 + 4 + 4 + (1 if num_bytes == 4 else 0)
                f.seek(pos)
                f.write(int(settings[k]).to_bytes(num_bytes, "little")) 

            f.seek(0)
            return f.read()


SAVE_SETTINGS = {
    "Sleeps Remaining": "IntProperty",
    "Beds Remaining": "IntProperty",
    "Unlocked Sleeping": "BoolProperty",
    "WakeUpId": "IntProperty"
}
