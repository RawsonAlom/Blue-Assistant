from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

REQUIRED_FILES = [
    "AGENTS.md",
    "PROJECT_CONTEXT.md",
    "PROJECT_STATUS.md",
    "ARCHITECTURE.md",
    "AI_WORKFLOW.md",
]

BUILDER = ROOT / "scripts" / "build_context.py"
REPORT = ROOT / "build" / "AI_CONTEXT.txt"


def check(condition: bool, message: str) -> bool:
    print(f"{'PASS' if condition else 'FAIL'}: {message}")
    return condition


def run(command: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )


def main() -> int:
    failures = 0

    print("========== BLUE PROJECT VERIFICATION ==========")

    for filename in REQUIRED_FILES:
        path = ROOT / filename
        if not check(
            path.is_file() and path.stat().st_size > 0,
            f"Required file: {filename}",
        ):
            failures += 1

    if not check(BUILDER.is_file(), "Context Builder exists"):
        failures += 1
        print(f"\nRESULT: FAILED ({failures} check(s)).")
        return 1

    syntax = run([
        sys.executable, "-m", "py_compile", str(BUILDER)
    ])

    if not check(syntax.returncode == 0, "Context Builder syntax"):
        print(syntax.stdout, end="")
        print(syntax.stderr, file=sys.stderr, end="")
        failures += 1

    if failures:
        print(f"\nRESULT: FAILED ({failures} check(s)).")
        return 1

    try:
        build = run([sys.executable, str(BUILDER)])
    except (OSError, subprocess.TimeoutExpired) as exc:
        print(f"FAIL: Context generation could not complete: {exc}")
        return 1

    if build.stdout:
        print(build.stdout, end="")
    if build.stderr:
        print(build.stderr, file=sys.stderr, end="")

    if not check(build.returncode == 0, "Context generation command"):
        failures += 1

    if not check(
        REPORT.is_file() and REPORT.stat().st_size > 0,
        "Context report exists",
    ):
        failures += 1
    else:
        content = REPORT.read_text(
            encoding="utf-8", errors="replace"
        )

        for filename in REQUIRED_FILES:
            if not check(
                f"## FILE: {filename}" in content,
                f"Context includes {filename}",
            ):
                failures += 1

    ignored = run([
        "git", "check-ignore", "-q", "build/AI_CONTEXT.txt"
    ])

    if not check(
        ignored.returncode == 0,
        "Generated context report is ignored by Git",
    ):
        failures += 1

    print()
    if failures:
        print(f"RESULT: FAILED ({failures} check(s)).")
        return 1

    print("RESULT: ALL CHECKS PASSED.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
