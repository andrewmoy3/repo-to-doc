from __future__ import annotations

import logging
import re
from pathlib import Path

log = logging.getLogger(__name__)

START = r"<!-- repodoc:auto:start:[\w-]+ -->"
END   = r"<!-- repodoc:auto:end:[\w-]+ -->"
BLOCK = re.compile(f"({START}.*?{END})", re.DOTALL)
SECTION = re.compile(r"(#{1,6} [^\n]+\n" + START + r".*?" + END + r")", re.DOTALL)
HEADING = re.compile(r"^(#{1,6} .+)$", re.MULTILINE)


def _inject_markers(markdown: str) -> str:
    """
    injects markers for ai generated sections. It identifies headings in the markdown and wraps the content under each heading with repodoc auto markers. The block_num is used to create unique markers for each section. 
    """
    if BLOCK.search(markdown):
        return markdown

    parts = HEADING.split(markdown)
    result = [parts[0]]

    for i, block_num in zip(range(1, len(parts), 2), range(1, len(parts))):
        heading = parts[i]
        content = parts[i + 1] if i + 1 < len(parts) else ""
        result.append(f"{heading}\n<!-- repodoc:auto:start:{block_num} -->\n{content.strip()}\n<!-- repodoc:auto:end:{block_num} -->\n\n")
        # result.append(f"{heading}\n<!-- repodoc:auto:start:{block_num} -->\n\n<!-- repodoc:auto:end:{block_num} -->\n\n")

    return "".join(result)


def _write_idempotent(path: Path, new_markdown: str) -> None:
    """
    Writes markdown to the given path, replacing only the sections between repodoc auto markers. This allows users to add custom notes outside of the auto-generated sections without worrying about their notes being overwritten on subsequent runs. Identifies AI generated blocks and replaces them by index.

    AI Generated function treated as black box.
    """
    # identify if note already exists
    existing = path.read_text() if path.exists() else ""

    # if it doesn't exist, just write the new markdown and return
    if not existing or not SECTION.search(existing):
        path.write_text(new_markdown)
        return

    new_sections = [m.group() for m in SECTION.finditer(new_markdown)]
    idx = 0

    def replace_section(m: re.Match) -> str:
        nonlocal idx
        if idx < len(new_sections):
            section = new_sections[idx]
            idx += 1
            return section
        return m.group()

    result = SECTION.sub(replace_section, existing)

    # append any new sections that didn't have a match in the existing file
    if idx < len(new_sections):
        result = result.rstrip("\n") + "\n\n" + "\n\n".join(new_sections[idx:]) + "\n"

    path.write_text(result)


def write(doc: dict, output_path: str) -> None:
    output_path = Path(output_path)
    output_path.mkdir(parents=True, exist_ok=True)
    path = output_path / f"{doc['name']}.md"

    # inject markers takes new doc, wraps content in markers corresponding 
    # to its header
    # write idempotent takes that new doc, breaks it down into blocks,
    # overwrites existing doc block by block by index
    _write_idempotent(path, _inject_markers(doc["markdown"]))
    log.info("Documentation successfully written to %s", path)
