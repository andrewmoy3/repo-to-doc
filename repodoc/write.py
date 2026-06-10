from __future__ import annotations

import logging
import re
from pathlib import Path

log = logging.getLogger(__name__)

START = r"<!-- repodoc:auto:start:[\w-]+ -->"
END   = r"<!-- repodoc:auto:end:[\w-]+ -->"
BLOCK = re.compile(f"({START}.*?{END})", re.DOTALL)
HEADING = re.compile(r"^(## .+)$", re.MULTILINE)


def _slugify(text: str) -> str:
    return re.sub(r"-+", "-", re.sub(r"[^\w]+", "-", text.lower())).strip("-")


def _inject_markers(markdown: str) -> str:
    if BLOCK.search(markdown):
        return markdown

    parts = HEADING.split(markdown)
    result = [parts[0]]
    for i in range(1, len(parts), 2):
        heading = parts[i]
        content = parts[i + 1] if i + 1 < len(parts) else ""
        name = _slugify(heading.lstrip("#").strip())
        result.append(f"{heading}\n<!-- repodoc:auto:start:{name} -->\n{content.strip()}\n<!-- repodoc:auto:end:{name} -->\n\n")
    return "".join(result)


def _write_idempotent(path: Path, new_markdown: str) -> None:
    """
    Writes markdown to the given path, replacing only the sections between repodoc auto markers. This allows users to add custom notes outside of the auto-generated sections without worrying about their notes being overwritten on subsequent runs. Identifies AI generated blocks and replaces them by index.

    AI Generated function treated as black box.
    """
    # print(new_markdown)
    # identify if note already exists
    existing = path.read_text() if path.exists() else ""

    # if it doesn't exist, just write the new markdown and return
    if not existing or not BLOCK.search(existing):
        path.write_text(new_markdown)
        return

    # find all blocks in the new markdown to be injected
    new_blocks = [m.group() for m in BLOCK.finditer(new_markdown)]
    idx = 0

    def replace_block(m: re.Match) -> str:
        nonlocal idx
        if idx < len(new_blocks):
            block = new_blocks[idx]
            idx += 1
            return block
        return m.group()

    # regex matching with 'BLOCK' pattern, replaces each match with corresponding
    # index block from new blocks list
    result = BLOCK.sub(replace_block, existing)
    path.write_text(result)


def write(doc: dict, output_path: str) -> None:
    output_path = Path(output_path)
    output_path.mkdir(parents=True, exist_ok=True)
    path = output_path / f"{doc['name']}.md"
    _write_idempotent(path, _inject_markers(doc["markdown"]))
    log.info("Documentation successfully written to %s", path)
