from .base import Room

ROOM = Room(
    id=1,
    title="THE MEMORY VAULT",
    flavor=(
        "The script builds a list of 5 million squared numbers before doing anything.\n"
        "Make it lazy — process one number at a time using yield.\n"
        "Door opens when peak memory drops below 1 MB."
    ),
    measure="memory",
    threshold=1.0,
    broken_label="~150 MB",
    fixed_label="< 1 MB",
    expected_output="41666654166667500000",
    hint1="get_numbers doesn't need to return a list. Can it hand back one number at a time instead?",
    hint2="Replace 'return [x * x for x in range(...)]' with a for loop that uses 'yield x * x'.",
    required_calls=["get_numbers", "process"],
    required_yields=["get_numbers"],
    code="""\
def get_numbers():
    # Builds the entire list in memory at once
    return [x * x for x in range(5_000_000)]

def process():
    total = 0
    for n in get_numbers():
        total += n
    return total

result = process()
print(f"Sum: {result}")
""",
)
