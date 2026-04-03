import asyncio

from .base import Room

# These are the real implementations — injected into the exec namespace so
# the user can't change their behaviour by editing the starter code.
async def _fetch_page_1():
    await asyncio.sleep(2)
    return "page 1"

async def _fetch_page_2():
    await asyncio.sleep(2)
    return "page 2"

async def _fetch_page_3():
    await asyncio.sleep(2)
    return "page 3"

_LOCKED_FNS = {
    "fetch_page_1": _fetch_page_1,
    "fetch_page_2": _fetch_page_2,
    "fetch_page_3": _fetch_page_3,
}

ROOM = Room(
    id=2,
    title="THE WAITING ROOM",
    flavor=(
        "Three pages are fetched one after another.\n"
        "The door opens when total runtime drops below 2.5 seconds.\n"
        "Right now it takes ~6 seconds. They don't need to wait for each other."
    ),
    measure="time",
    threshold=2.5,
    broken_label="~6.0s",
    fixed_label="< 2.5s",
    hint1="All three fetches are independent. asyncio has a way to run coroutines side by side...",
    hint2="Replace the three separate awaits with:\n  a, b, c = await asyncio.gather(fetch_page_1(), fetch_page_2(), fetch_page_3())",
    required_calls=["fetch_page_1", "fetch_page_2", "fetch_page_3", "gather"],
    locked_fns=_LOCKED_FNS,
    code="""\
import asyncio

async def fetch_page_1():
    await asyncio.sleep(2)
    return "page 1"

async def fetch_page_2():
    await asyncio.sleep(2)
    return "page 2"

async def fetch_page_3():
    await asyncio.sleep(2)
    return "page 3"

async def main():
    a = await fetch_page_1()
    b = await fetch_page_2()
    c = await fetch_page_3()
    return [a, b, c]

result = asyncio.run(main())
print(result)
""",
)
