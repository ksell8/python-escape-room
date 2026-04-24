# Python Escape Room

A game for learning Python concepts through six increasingly challenging puzzles.
Each room presents broken code — fix it to unlock the door.

## Setup

Requires Python 3.11+ and [uv](https://docs.astral.sh/uv/).

```bash
uv sync
```

## Run without building

```bash
uv run app.py
```

## Build the macOS app 

#### Claude added the other major OSes, but was too lazy to test :shrug: :shamrock:

```bash
uv run build.py
```

Produces `dist/PythonEscapeRoom.app`. Drag it to Applications or double-click to play.

## Rooms

| # | Title | Concept |
|---|-------|---------|
| 0a | The Override | Subclassing — override a base class method |
| 0b | The Contract | Abstract base classes (`ABC`, `@abstractmethod`) |
| 1 | The Waiting Room | `asyncio.gather` — run coroutines concurrently |
| 2 | The Memory Vault | Generators — `yield` instead of building a list |
| 3 | The Spider's Web | Async generators — `async def` + `yield` |
| 4 | The Final Lock | Twisted `DeferredQueue` + `gatherResults` (how Scrapy works under the hood) |

## Project structure

```
app.py          — tkinter UI
build.py        — builds PythonEscapeRoom.app via PyInstaller
rooms/
  __init__.py   — public interface (ROOMS, Room, RunResult, run_room)
  base.py       — Pydantic models (Room, RunResult)
  runner.py     — code execution engine and AST helpers
  room_0a.py    — The Override
  room_0b.py    — The Contract
  room_1.py     — The Waiting Room
  room_2.py     — The Memory Vault
  room_3.py     — The Spider's Web
  room_4.py     — The Final Lock
```
