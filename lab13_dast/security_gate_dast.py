from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


SEVERITY_ORDER = {
    "INFO": 0,
    "LOW": 1,
    "MEDIUM": 2,
    "HIGH": 3,
    "CRITICAL": 4,
}


def read_text(path: Path) -> str:
    if not path.exists():
        raise FileNotFoundError(f"Файл не найден: {path}")
    return path.read_text(encoding="utf-8", errors="replace")


def load_ignore_patterns(ignore_file: Path | None) -> list[str]:
    if ignore_file is None or not ignore_file.exists():
        return []

    patterns: list[str] = []
    for line in ignore_file.read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        patterns.append(line)
    return patterns


def apply_ignore_rules(text: str, patterns: list[str]) -> str:
    if not patterns:
        return text

    filtered_lines: list[str] = []
    for line in text.splitlines():
        if any(pattern in line for pattern in patterns):
            continue
        filtered_lines.append(line)

    return "\n".join(filtered_lines)


def read_pytest_exit_code(exit_code_file: Path) -> int:
    if not exit_code_file.exists():
        print(f"[security-gate] Файл exit code не найден: {exit_code_file}")
        return 1

    raw_value = exit_code_file.read_text(encoding="utf-8", errors="replace").strip()
    try:
        return int(raw_value)
    except ValueError:
        print(f"[security-gate] Некорректный exit code: {raw_value}")
        return 1


def find_dast_severity_markers(text: str) -> list[str]:
    """
    Для демонстрации блокировки Security Gate поддерживаются явные маркеры:
    DAST_SEVERITY=HIGH
    DAST_SEVERITY=CRITICAL
    """
    pattern = re.compile(r"DAST_SEVERITY\s*[:=]\s*(INFO|LOW|MEDIUM|HIGH|CRITICAL)", re.IGNORECASE)
    return [match.group(1).upper() for match in pattern.finditer(text)]


def main() -> int:
    parser = argparse.ArgumentParser(description="Security Gate для DAST-отчёта pytest")
    parser.add_argument("--report", required=True, help="Путь к текстовому DAST-отчёту")
    parser.add_argument("--exit-code-file", required=True, help="Файл с exit code pytest")
    parser.add_argument("--threshold", default="high", choices=["info", "low", "medium", "high", "critical"])
    parser.add_argument("--ignore-file", default=None, help="Файл с шаблонами ложных срабатываний")
    args = parser.parse_args()

    report_path = Path(args.report)
    exit_code_path = Path(args.exit_code_file)
    ignore_file = Path(args.ignore_file) if args.ignore_file else None

    threshold = args.threshold.upper()
    threshold_value = SEVERITY_ORDER[threshold]

    original_report = read_text(report_path)
    ignore_patterns = load_ignore_patterns(ignore_file)
    report = apply_ignore_rules(original_report, ignore_patterns)

    pytest_exit_code = read_pytest_exit_code(exit_code_path)
    severity_markers = find_dast_severity_markers(report)

    blocking_markers = [
        severity for severity in severity_markers
        if SEVERITY_ORDER[severity] >= threshold_value
    ]

    print("[security-gate] DAST Security Gate")
    print(f"[security-gate] Report: {report_path}")
    print(f"[security-gate] Pytest exit code: {pytest_exit_code}")
    print(f"[security-gate] Threshold: {threshold}")
    print(f"[security-gate] Ignore rules: {len(ignore_patterns)}")
    print(f"[security-gate] DAST severity markers: {severity_markers if severity_markers else 'none'}")

    if pytest_exit_code != 0:
        print("[security-gate] FAILED: DAST-тесты завершились с ошибкой.")
        return 1

    if blocking_markers:
        print(f"[security-gate] FAILED: найдены блокирующие DAST-находки: {blocking_markers}")
        return 1

    print("[security-gate] PASSED: блокирующих DAST-находок не обнаружено.")
    return 0


if __name__ == "__main__":
    sys.exit(main())