#!/usr/bin/env python3
from __future__ import annotations

import html
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "Migalha-Guilherme-Menezes.md"
OUTPUT = ROOT / "index.html"


def cross_words(fragment: str) -> str:
    protected: list[str] = []

    def protect(match: re.Match[str]) -> str:
        protected.append(match.group(0))
        return f"@@EXPLICIT_CROSS_{len(protected) - 1}@@"

    fragment = re.sub(
        r"<ruby>(?:Cristo|cruz)<rt>✝︎</rt></ruby>",
        protect,
        fragment,
    )

    parts = re.split(r"(<[^>]+>)", fragment)
    for index in range(0, len(parts), 2):
        parts[index] = re.sub(
            r"(?<![\wÀ-ÿ])(Deus|Cristo|cruz)(?![\wÀ-ÿ])",
            r'<span class="cross-word">\1</span>',
            parts[index],
        )
    fragment = "".join(parts)

    for index, value in enumerate(protected):
        fragment = fragment.replace(f"@@EXPLICIT_CROSS_{index}@@", value)
    return fragment


def parse_source(text: str) -> tuple[str, str, str, list[str]]:
    lines = text.splitlines()
    title = lines[0].removeprefix("# ").strip()
    author = lines[2].strip().strip("*")

    epigraph_lines: list[str] = []
    cursor = 4
    while cursor < len(lines) and lines[cursor].startswith(">"):
        value = lines[cursor].removeprefix(">").strip()
        if value:
            epigraph_lines.append(value)
        cursor += 1

    epigraph = " ".join(epigraph_lines)
    epigraph = re.sub(r"^\*(.+)\*\s+—\s+", r"<em>\1</em><cite>— ", epigraph)
    if "<cite>" in epigraph:
        epigraph += "</cite>"

    while cursor < len(lines) and (not lines[cursor].strip() or lines[cursor].strip() == "---"):
        cursor += 1

    blocks: list[str] = []
    current: list[str] = []
    for line in lines[cursor:]:
        if line.strip():
            current.append(line.strip())
        elif current:
            blocks.append(" ".join(current))
            current = []
    if current:
        blocks.append(" ".join(current))

    return title, author, epigraph, blocks


def render() -> str:
    title, author, epigraph, blocks = parse_source(SOURCE.read_text(encoding="utf-8"))
    paragraphs = "\n".join(f"        <p>{cross_words(block)}</p>" for block in blocks)
    description = (
        "Conto de Guilherme Menezes em edição digital com anotações ruby, "
        "microdiagramas tipográficos e leitura integral."
    )
    return f"""<!doctype html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="author" content="{html.escape(author)}">
  <meta name="description" content="{html.escape(description)}">
  <meta name="copyright" content="© 2026 Guilherme Menezes. Todos os direitos reservados.">
  <meta property="og:type" content="article">
  <meta property="og:title" content="{html.escape(title)}">
  <meta property="og:description" content="{html.escape(description)}">
  <title>{html.escape(title)} | {html.escape(author)}</title>
  <link rel="stylesheet" href="styles.css">
</head>
<body>
  <main>
    <header class="title-page">
      <h1>{html.escape(title)}</h1>
      <p class="author">{html.escape(author)}</p>
      <blockquote>{epigraph}</blockquote>
    </header>

    <article>
{paragraphs}
    </article>

    <footer>
      <p><cite>{html.escape(title)}</cite>, de {html.escape(author)}.</p>
      <p>Primeira publicação digital: 25 de julho de 2026.</p>
      <p>© 2026 Guilherme Menezes. Todos os direitos reservados.</p>
      <nav aria-label="Arquivos da obra">
        <a href="Migalha-Guilherme-Menezes.pdf">PDF</a>
        <a href="Migalha-Guilherme-Menezes.md">Markdown</a>
        <span class="doi">DOI pendente</span>
      </nav>
    </footer>
  </main>
</body>
</html>
"""


if __name__ == "__main__":
    OUTPUT.write_text(render(), encoding="utf-8")
    print(OUTPUT)
