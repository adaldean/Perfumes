#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
from pathlib import Path

MULTILINE_VAR_RE = re.compile(r"\{\{\s*\n\s*(.*?)\s*\}\}", re.DOTALL)


def collapse_multiline_vars(content: str) -> tuple[str, int]:
    replacements = 0

    def _replace(match: re.Match[str]) -> str:
        nonlocal replacements
        replacements += 1
        expression = re.sub(r"\s+", " ", match.group(1)).strip()
        return f"{{{{ {expression} }}}}"

    updated = MULTILINE_VAR_RE.sub(_replace, content)
    return updated, replacements


def process_file(path: Path, fix: bool) -> int:
    original = path.read_text(encoding="utf-8")
    updated, changes = collapse_multiline_vars(original)

    if fix and changes > 0:
        path.write_text(updated, encoding="utf-8")

    return changes


def iter_templates(root: Path):
    templates_dir = root / "templates"
    if not templates_dir.exists():
        return []
    return sorted(templates_dir.rglob("*.html"))


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Detecta y corrige expresiones Django '{{ ... }}' partidas en múltiples líneas."
    )
    parser.add_argument("--fix", action="store_true", help="Aplica correcciones en archivos")
    args = parser.parse_args()

    root = Path(__file__).resolve().parent.parent
    files = iter_templates(root)

    total = 0
    affected = []

    for file_path in files:
        count = process_file(file_path, fix=args.fix)
        if count > 0:
            total += count
            affected.append((file_path, count))

    mode = "FIX" if args.fix else "CHECK"
    if affected:
        print(f"[{mode}] Se encontraron {total} expresión(es) multilinea en {len(affected)} archivo(s):")
        for file_path, count in affected:
            rel = file_path.relative_to(root)
            print(f" - {rel}: {count}")
        if not args.fix:
            print("\nUsa --fix para corregir automáticamente.")
            return 1
        return 0

    print(f"[{mode}] Sin expresiones multilinea '{{{{ ... }}}}' en templates.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
