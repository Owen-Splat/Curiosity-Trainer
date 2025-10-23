import sys, os, json

VERSION = "0.2.0"

# check if running from source
if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
    from sys import _MEIPASS
    IS_RUNNING_FROM_SOURCE = False
    ROOT_PATH = _MEIPASS
else:
    IS_RUNNING_FROM_SOURCE = True
    ROOT_PATH = os.path.dirname(os.path.realpath(__file__))

DEFAULT_POSITIONS = {
    'Ascent': (-29.387, 11.706, 81.655),
    'Statue Climb': (46.809, -22.663, 161.979),
    'Aquarium': (42.489, 46.42, 179.82),
    'Trip': (44.305, -64.8, 461.068),
    'Hands': (74.052, -32.992, 787.192),
    'Coffin Skip': (14.69, -139.528, 1017.391),
    'Amphitheater': (127.802, 241.105, 1217.092),
    'Lasers': (-45.762, -25.119, 1901.672)
}

POSITION_FILE_PATH = os.path.join(ROOT_PATH, "pos.json")
if os.path.exists(POSITION_FILE_PATH):
    with open(POSITION_FILE_PATH, 'r') as f:
        try:
            SAVED_POSITIONS = json.load(f)
        except json.JSONDecodeError:
            SAVED_POSITIONS = {}
else:
    SAVED_POSITIONS = {}

with open(os.path.join(ROOT_PATH, "assets", "theme.txt"), 'r') as f:
    THEME = f.read()
