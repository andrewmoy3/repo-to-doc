import logging
from pathlib import Path

log = logging.getLogger(__name__)

def write(doc, output_path):
    """
    Writes generated documentation to the specified output path.
    """
    output_path = Path(output_path)
    output_path.mkdir(parents=True, exist_ok=True)
    path = output_path / f"{doc['name']}.md"
    with open(path, "w") as f:
        doc_name = doc["name"]
        doc_markdown = doc["markdown"]
        # f.write(f"# {doc_name}\n\n")
        f.write(doc_markdown)
    log.info("Documentation successfully written to %s", path)
