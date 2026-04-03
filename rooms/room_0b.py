from .base import Room


ROOM = Room(
    id="0b",
    title="THE CONTRACT",
    flavor=(
        "Same door, stricter rules. Now Door uses ABC and @abstractmethod.\n"
        "Python won't even let you instantiate a class that skips the contract.\n"
        "Implement the abstract method to satisfy the contract and escape."
    ),
    measure="time",
    threshold=5.0,
    broken_label="crashes",
    fixed_label="runs clean",
    expected_output="OPEN",
    required_calls=["open"],
    required_subclass="Door",
    hint1="ABC means Abstract Base Class. You can't instantiate it directly — you must subclass it and implement every @abstractmethod.",
    hint2="class EscapeDoor(Door):\n    def open(self):\n        return 'OPEN'\n\nrun_engine(EscapeDoor())",
    code="""\
from abc import ABC, abstractmethod

class Door(ABC):
    @abstractmethod
    def open(self):
        pass  # No implementation — subclasses MUST provide one

# The engine that controls the door — do not modify
def run_engine(door):
    result = door.open()
    print(result)

# TODO: subclass Door and implement open() to return "OPEN"
# Notice: you can't even instantiate Door() directly now — try it and see

run_engine(Door())  # replace Door() with your subclass
""",
)
