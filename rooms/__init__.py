"""
rooms/ — Public interface for the escape room puzzle engine.

Imports here mirror the old rooms.py so app.py needs no changes:
    from rooms import ROOMS, Room, RunResult, run_room
"""

from .base import Room, RunResult
from .runner import run_room
from .room_0a import ROOM as _room_0a
from .room_0b import ROOM as _room_0b
from .room_1 import ROOM as _room_1
from .room_2 import ROOM as _room_2
from .room_3 import ROOM as _room_3
from .room_4 import ROOM as _room_4

ROOMS: list[Room] = [
    _room_0a,
    _room_0b,
    _room_1,
    _room_2,
    _room_3,
    _room_4,
]

__all__ = ["ROOMS", "Room", "RunResult", "run_room"]
