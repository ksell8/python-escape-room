from .base import Room


ROOM = Room(
    id="0a",
    title="THE OVERRIDE",
    flavor=(
        "A Door base class has open() — but it just raises NotImplementedError.\n"
        "The engine calls door.open() to escape. It keeps crashing.\n"
        "Subclass Door and override open() to return 'OPEN'. Unlock the door."
    ),
    measure="time",
    threshold=5.0,
    broken_label="crashes",
    fixed_label="runs clean",
    expected_output="OPEN",
    required_calls=["open"],
    required_subclass="Door",
    hint1="The engine takes a door and tries to open it. The Door class doesn't open, but you can subclass it and override open.",
    hint2="class EscapeDoor(Door):\n    def open(self):\n        return 'OPEN'",
    code="""\
class Door:
    def open(self):
        raise NotImplementedError("Subclass must implement open()")

# The engine that controls the door — do not modify
def run_engine(door):
    result = door.open()
    print(result)

# TODO: subclass Door and override open() to return "OPEN"
# Then instantiate your subclass and pass it to run_engine()

run_engine(Door())  # replace Door() with your subclass
""",
)
