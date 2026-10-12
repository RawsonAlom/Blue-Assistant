from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUTPUT = ROOT / "build" / "AI_CONTEXT.txt"

BASE_FILES = [
    "AGENTS.md",
    "PROJECT_CONTEXT.md",
    "PROJECT_STATUS.md",
    "ARCHITECTURE.md",
    "AI_WORKFLOW.md",
]

MAX_FILE_CHARS = 40_000
MAX_TOTAL_CHARS = 180_000

BLOCKED_PARTS = {
    ".git", ".venv", "venv", "node_modules",
    "__pycache__", "build", "dist",
}

SENSITIVE_NAME = re.compile(
    r"(?i)(^\.env(?:\.|$)|secret|credential|password|"
    r"private.?key|access.?token)"
)

SECRET_ASSIGNMENT = re.compile(
    r"(?i)^(\s*(?:export\s+)?"
    r"[A-Z0-9_]*(?:API[_-]?KEY|ACCESS[_-]?TOKEN|"
    r"REFRESH[_-]?TOKEN|CLIENT[_-]?SECRET|PASSWORD|"
    r"PASSWD|SECRET[_-]?KEY|PRIVATE[_-]?KEY|AUTHORIZATION)"
    r"[A-Z0-9_]*\s*[:=]\s*)(.*)$"
)

KNOWN_TOKENS = [
    (
        re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b"),
        "[REDACTED_API_KEY]",
    ),
    (
        re.compile(r"\bgh[pousr]_[A-Za-z0-9_]{20,}\b"),
        "[REDACTED_GITHUB_TOKEN]",
    ),
    (
        re.compile(r"\bAKIA[A-Z0-9]{16}\b"),
        "[REDACTED_ACCESS_KEY]",
    ),
    (
        re.compile(
            r"(?i)(Bearer\s+)[A-Za-z0-9._~+/=-]{20,}"
        ),
        r"\1[REDACTED_TOKEN]",
    ),
]


def git_output(*args: str) -> str:
    """Return Git information without failing if a command is unavailable."""
    try:
        result = subprocess.run(
            ["git", *args],
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
        return (result.stdout or result.stderr).strip()
    except (OSError, subprocess.TimeoutExpired) as exc:
        return f"Unavailable: {exc}"


def redact_secrets(text: str) -> str:
    """Redact common credentials before content enters the context bundle."""
    text = re.sub(
        r"-----BEGIN [^-]*PRIVATE KEY-----.*?"
        r"-----END [^-]*PRIVATE KEY-----",
        "[REDACTED PRIVATE KEY]",
        text,
        flags=re.DOTALL,
    )

    for pattern, replacement in KNOWN_TOKENS:
        text = pattern.sub(replacement, text)

    safe_lines = []

    for line in text.splitlines():
        match = SECRET_ASSIGNMENT.match(line)

        if match:
            prefix, rhs = match.groups()
            lower_rhs = rhs.lower()

            # Preserve code that reads a secret from environment/config.
            env_references = (
                "os.getenv", "os.environ", "getenv(",
                "environ[", "settings.",
            )

            if not any(ref in lower_rhs for ref in env_references):
                value = rhs.strip()

                if value.startswith(("'", '"')):
                    quote = value[0]
                    end = value.find(quote, 1)

                    if end > 1:
                        actual_value = value[1:end].strip().lower()
                        placeholders = (
                            "", "none", "null", "example",
                            "placeholder", "your_api_key",
                            "your-secret-here",
                        )

                        if actual_value not in placeholders:
                            suffix = value[end + 1:]
                            line = (
                                prefix + quote + "[REDACTED]" +
                                quote + suffix
                            )

                else:
                    candidate = value.split("#", 1)[0].strip()

                    if re.fullmatch(r"[A-Za-z0-9_+/=-]{16,}", candidate):
                        line = prefix + "[REDACTED]"

        safe_lines.append(line)

    return "\n".join(safe_lines)


def read_project_file(relative_path: str) -> str:
    """Read an explicitly selected, safe, reasonably sized text file."""
    candidate = Path(relative_path)

    if candidate.is_absolute():
        raise ValueError("Use project-relative paths, not absolute paths.")

    resolved = (ROOT / candidate).resolve()

    try:
        resolved.relative_to(ROOT.resolve())
    except ValueError:
        raise ValueError("The selected file is outside the project.")

    parts = candidate.parts

    if (
        any(part in BLOCKED_PARTS for part in parts)
        or any(SENSITIVE_NAME.search(part) for part in parts)
    ):
        raise ValueError("Sensitive or generated paths cannot be included.")

    if not resolved.is_file():
        raise ValueError(f"File does not exist: {relative_path}")

    if resolved.stat().st_size > MAX_FILE_CHARS * 4:
        raise ValueError(f"File is too large: {relative_path}")

    raw = resolved.read_bytes()

    if b"\0" in raw:
        raise ValueError(f"Binary files are not supported: {relative_path}")

    content = raw.decode("utf-8", errors="replace")
    content = redact_secrets(content)

    if len(content) > MAX_FILE_CHARS:
        content = (
            content[:MAX_FILE_CHARS]
            + "\n\n[TRUNCATED: file character limit reached]\n"
        )

    return content


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Build a secret-conscious BLUE context bundle for AI review."
    )
    parser.add_argument(
        "--file",
        action="append",
        default=[],
        metavar="PATH",
        help="Add a relevant project-relative source file; repeat as needed.",
    )
    args = parser.parse_args()

    sections: list[str] = [
        "# BLUE — AI Context Bundle",
        "",
        "Generated from the current local repository.",
        "Review the actual source files before making code changes.",
        "",
        "## Repository Status",
        git_output("status", "--short", "--branch"),
        "",
        "## Recent Git History",
        git_output("log", "-5", "--oneline"),
        "",
        "## Unstaged Diff Summary",
        git_output("diff", "--stat") or "No unstaged tracked changes.",
        "",
        "## Staged Diff Summary",
        git_output("diff", "--cached", "--stat")
        or "No staged tracked changes.",
    ]

    selected_files = list(BASE_FILES)

    for filename in args.file:
        if filename not in selected_files:
            selected_files.append(filename)

    skipped_files = 0

    for filename in selected_files:
        candidate = ROOT / filename

        if filename not in BASE_FILES and not candidate.exists():
            print(
                f"WARNING: optional source file not found; skipped: {filename}",
                file=sys.stderr,
            )
            skipped_files += 1
            continue

        try:
            content = read_project_file(filename)
        except (OSError, ValueError) as exc:
            print(f"ERROR: {filename}: {exc}", file=sys.stderr)
            return 1

        sections.extend([
            "",
            "=" * 72,
            f"## FILE: {filename}",
            "=" * 72,
            content,
        ])

    report = "\n".join(sections).rstrip() + "\n"

    if len(report) > MAX_TOTAL_CHARS:
        report = (
            report[:MAX_TOTAL_CHARS]
            + "\n\n[TRUNCATED: total context size limit reached]\n"
        )

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(report, encoding="utf-8")

    print("PASS: Context bundle created.")
    print(f"Output: {OUTPUT.relative_to(ROOT)}")
    print(f"Characters: {len(report):,}")
    print(f"Base documents: {len(BASE_FILES)}")
    print(f"Additional source files requested: {len(args.file)}")
    print(f"Additional source files skipped (not found): {skipped_files}")
    print()
    print("Security reminder:")
    print("- Never upload secrets or credentials to an AI service.")
    print("- Review the generated bundle before sharing it.")
    print("- Secret-pattern filtering cannot guarantee detection of every secret.")
    print("- Relevant source files must be selected explicitly with --file.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
