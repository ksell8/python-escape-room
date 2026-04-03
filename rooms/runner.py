"""
runner.py — Code execution engine and AST inspection helpers.
No room definitions or UI code here.
"""

import ast
import io
import sys
import time
import traceback
import tracemalloc

from .base import Room, RunResult


def _fn_contains_yield(code: str, fn_name: str) -> bool:
    """Return True if the named function contains a yield statement."""
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return False
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if node.name == fn_name:
                for child in ast.walk(node):
                    if isinstance(child, (ast.Yield, ast.YieldFrom)):
                        return True
    return False


def _has_subclass_of(code: str, base_name: str) -> bool:
    """Return True if the code contains any class definition that inherits from base_name."""
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return False
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            for base in node.bases:
                if isinstance(base, ast.Name) and base.id == base_name:
                    return True
    return False


def _get_called_names(code: str) -> set[str]:
    """Return the set of all function/method names called in the code."""
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return set()
    called = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                called.add(node.func.id)
            elif isinstance(node.func, ast.Attribute):
                called.add(node.func.attr)
    return called


def run_room(room: Room, code: str) -> RunResult:
    """
    Execute user-supplied code string, capture stdout/stderr,
    measure time and peak memory, return a RunResult.
    """
    output_lines: list[str] = []

    class Capture:
        def write(self, s: str):
            output_lines.append(s)
        def flush(self):
            pass

    old_stdout, old_stderr = sys.stdout, sys.stderr
    sys.stdout = Capture()
    sys.stderr = Capture()

    error: str | None = None
    tracemalloc.start()
    start = time.perf_counter()

    # Normalize any tab characters to 4 spaces before exec
    code = code.expandtabs(4)

    # Build exec namespace
    namespace: dict = {"__builtins__": __builtins__}
    if room.locked_fns:
        namespace.update(room.locked_fns)     # injected + tamper-checked

    # Snapshot locked fn ids before exec so we can detect tampering after
    locked_ids_before = {name: id(fn) for name, fn in (room.locked_fns or {}).items()}

    try:
        exec(compile(code, "<escape_room>", "exec"), namespace)
    except Exception as e:
        # Strip frames above <escape_room> so the user only sees their own error
        tb = e.__traceback__
        while tb and tb.tb_frame.f_code.co_filename != "<escape_room>":
            tb = tb.tb_next
        if tb:
            buf = io.StringIO()
            buf.write("Traceback (most recent call last):\n")
            traceback.print_tb(tb, file=buf)
            buf.write(f"{type(e).__name__}: {e}\n")
            error = buf.getvalue()
        else:
            error = traceback.format_exc()
    finally:
        elapsed = time.perf_counter() - start
        _, peak_bytes = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        sys.stdout = old_stdout
        sys.stderr = old_stderr

    # Detect if user redefined any locked functions
    tampered = [
        name for name, fn in (room.locked_fns or {}).items()
        if name in namespace and getattr(namespace[name], "__code__", None) is not None
           and namespace[name].__code__.co_code != fn.__code__.co_code
    ]

    peak_mb = peak_bytes / (1024 * 1024)
    output = "".join(output_lines)

    required_subclass_met = True
    if room.required_subclass:
        required_subclass_met = _has_subclass_of(code, room.required_subclass)

    required_calls_met = True
    if room.required_calls:
        called = _get_called_names(code)
        required_calls_met = all(fn in called for fn in room.required_calls)

    required_yields_met = True
    if room.required_yields:
        required_yields_met = all(_fn_contains_yield(code, fn) for fn in room.required_yields)

    failure_reason = ""
    tamper_warning = ""
    if tampered:
        tamper_warning = "🚨 DO NOT MODIFY: " + ", ".join(tampered) + " — your edits are ignored, the real versions ran"
    if error:
        passed = False
        failure_reason = "runtime error"
    elif not required_subclass_met:
        passed = False
        failure_reason = f"must subclass: {room.required_subclass}"
    elif not required_calls_met:
        passed = False
        missing = [fn for fn in room.required_calls if fn not in _get_called_names(code)]
        failure_reason = "must call: " + ", ".join(missing)
    elif not required_yields_met:
        passed = False
        missing = [fn for fn in room.required_yields if not _fn_contains_yield(code, fn)]
        failure_reason = ", ".join(missing) + " must use yield"
    elif room.measure == "time":
        output_ok = (room.expected_output == "") or (room.expected_output in output)
        passed = elapsed < room.threshold and output_ok
        if not passed:
            failure_reason = "wrong output" if not output_ok else f"too slow ({elapsed:.2f}s, need < {room.threshold}s)"
    elif room.measure == "memory":
        passed = peak_mb < room.threshold and room.expected_output in output
        if not passed:
            failure_reason = "wrong output" if room.expected_output not in output else f"too much memory ({peak_mb:.1f} MB, need < {room.threshold} MB)"
    else:  # both time and memory
        output_ok = (room.expected_output == "") or (room.expected_output in output)
        time_ok = elapsed < room.threshold
        mem_ok = peak_mb < room.memory_threshold
        passed = output_ok and time_ok and mem_ok
        if not passed:
            if not output_ok:
                failure_reason = "wrong output"
            elif not time_ok and not mem_ok:
                failure_reason = f"too slow ({elapsed:.2f}s) and too much memory ({peak_mb:.1f} MB)"
            elif not time_ok:
                failure_reason = f"too slow ({elapsed:.2f}s, need < {room.threshold}s)"
            else:
                failure_reason = f"too much memory ({peak_mb:.1f} MB, need < {room.memory_threshold} MB)"

    return RunResult(
        output=output,
        error=error,
        elapsed=elapsed,
        peak_memory_mb=peak_mb,
        passed=passed,
        failure_reason=failure_reason,
        tamper_warning=tamper_warning,
    )
