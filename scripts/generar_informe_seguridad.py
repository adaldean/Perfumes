#!/usr/bin/env python3
"""Genera el informe de auditoría de seguridad en PDF desde Markdown."""

from __future__ import annotations

import argparse
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    Paragraph,
    Preformatted,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
    HRFlowable,
)


def build_styles():
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="Body", parent=styles["Normal"], fontName="Helvetica", fontSize=10.5, leading=14))
    styles.add(ParagraphStyle(name="H1", parent=styles["Heading1"], fontName="Helvetica-Bold", fontSize=18, leading=22, spaceAfter=10))
    styles.add(ParagraphStyle(name="H2", parent=styles["Heading2"], fontName="Helvetica-Bold", fontSize=14, leading=18, spaceBefore=6, spaceAfter=6))
    styles.add(ParagraphStyle(name="H3", parent=styles["Heading3"], fontName="Helvetica-Bold", fontSize=12, leading=16, spaceBefore=4, spaceAfter=4))
    styles.add(ParagraphStyle(name="Mono", parent=styles["Code"], fontName="Courier", fontSize=8.8, leading=11))
    return styles


def _clean_inline(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace("**", "")
        .replace("`", "")
    )


def _table_from_lines(lines: list[str], styles):
    rows = []
    for line in lines:
        row = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if row:
            rows.append(row)

    # Eliminar separador markdown (---)
    filtered = []
    for row in rows:
        if all(set(cell.replace(":", "").replace("-", "").strip()) == set() for cell in row):
            continue
        filtered.append(row)

    if not filtered:
        return None

    data = [[Paragraph(_clean_inline(cell), styles["Body"]) for cell in row] for row in filtered]
    table = Table(data, repeatRows=1)
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#E9EEF5")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 5),
                ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    return table


def markdown_to_story(md_text: str):
    styles = build_styles()
    story = []

    lines = md_text.splitlines()
    i = 0
    in_code = False
    code_buffer: list[str] = []

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        if stripped.startswith("```"):
            if in_code:
                story.append(Preformatted("\n".join(code_buffer), styles["Mono"]))
                story.append(Spacer(1, 0.2 * cm))
                code_buffer = []
                in_code = False
            else:
                in_code = True
            i += 1
            continue

        if in_code:
            code_buffer.append(line)
            i += 1
            continue

        if stripped.startswith("|") and stripped.endswith("|"):
            table_lines = [line]
            j = i + 1
            while j < len(lines):
                nxt = lines[j].strip()
                if nxt.startswith("|") and nxt.endswith("|"):
                    table_lines.append(lines[j])
                    j += 1
                else:
                    break
            table = _table_from_lines(table_lines, styles)
            if table:
                story.append(table)
                story.append(Spacer(1, 0.25 * cm))
            i = j
            continue

        if not stripped:
            story.append(Spacer(1, 0.16 * cm))
            i += 1
            continue

        if stripped == "---":
            story.append(HRFlowable(color=colors.grey, thickness=0.5, width="100%"))
            story.append(Spacer(1, 0.2 * cm))
            i += 1
            continue

        if stripped.startswith("# "):
            story.append(Paragraph(_clean_inline(stripped[2:].strip()), styles["H1"]))
            i += 1
            continue
        if stripped.startswith("## "):
            story.append(Paragraph(_clean_inline(stripped[3:].strip()), styles["H2"]))
            i += 1
            continue
        if stripped.startswith("### "):
            story.append(Paragraph(_clean_inline(stripped[4:].strip()), styles["H3"]))
            i += 1
            continue

        if stripped.startswith("- "):
            story.append(Paragraph(f"• {_clean_inline(stripped[2:])}", styles["Body"]))
            i += 1
            continue

        if stripped.startswith(("1. ", "2. ", "3. ", "4. ", "5. ", "6. ", "7. ", "8. ", "9. ")):
            story.append(Paragraph(_clean_inline(stripped), styles["Body"]))
            i += 1
            continue

        story.append(Paragraph(_clean_inline(stripped), styles["Body"]))
        i += 1

    return story


def add_page_number(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 9)
    canvas.drawRightString(A4[0] - 2 * cm, 1.2 * cm, f"Página {doc.page}")
    canvas.restoreState()


def generate_pdf(input_md: Path, output_pdf: Path):
    md_text = input_md.read_text(encoding="utf-8")
    story = markdown_to_story(md_text)

    output_pdf.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(
        str(output_pdf),
        pagesize=A4,
        leftMargin=2 * cm,
        rightMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
        title="Informe de Auditoría SQLi y Seguridad",
        author="Copilot Coding Agent",
    )
    doc.build(story, onFirstPage=add_page_number, onLaterPages=add_page_number)


def parse_args():
    parser = argparse.ArgumentParser(description="Generar informe PDF de auditoría de seguridad")
    parser.add_argument(
        "--input",
        type=Path,
        default=Path("docs/informe_auditoria_sqli_seguridad.md"),
        help="Ruta del markdown fuente",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("docs/informe_auditoria_sqli_seguridad.pdf"),
        help="Ruta del PDF de salida",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    generate_pdf(args.input, args.output)
    print(f"PDF generado correctamente en: {args.output}")


if __name__ == "__main__":
    main()
