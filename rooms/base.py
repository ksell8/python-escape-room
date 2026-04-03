"""
base.py — Pydantic models shared across all rooms.
"""

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict


class RunResult(BaseModel):
    output: str
    error: str | None
    elapsed: float        # seconds (always measured)
    peak_memory_mb: float # MB (always measured, 0 if not relevant)
    passed: bool
    failure_reason: str = ""  # human-readable reason if passed=False
    tamper_warning: str = ""  # set if user redefined a locked function


class Room(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    id: int | str
    title: str
    flavor: str
    code: str
    hint1: str
    hint2: str
    measure: Literal["time", "memory", "both"]
    threshold: float      # seconds if measure=="time", MB if measure=="memory"
    memory_threshold: float = 0.0  # MB, only used when measure=="both"
    broken_label: str     # shown in UI as "baseline" e.g. "~6.0s" or "~150 MB"
    fixed_label: str      # shown in UI as "goal"    e.g. "~2.0s" or "< 1 MB"
    expected_output: str = ""  # if set, output must contain this string to pass
    required_calls: list[str] | None = None  # function names that must be called (checked via AST)
    required_yields: list[str] | None = None  # function names that must contain a yield statement
    locked_fns: dict[str, Any] | None = None    # name -> callable, injected + tamper-checked
    required_subclass: str | None = None        # class name student must subclass (checked via AST)
