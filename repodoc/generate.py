import anthropic
from pathlib import Path

import logging
log = logging.getLogger(__name__)

def gen_docs(scanned_repo: dict) -> str:
    """
    """
    template_file = Path(__file__).parent.parent / "template.md"
    with open(template_file, "r") as f:
        template = f.read()
    f.close()

    client = anthropic.Anthropic()

    def list_to_string(lst):
        return "\n".join(f"- {item}" for item in lst)

    if "error" in scanned_repo:
        log.error("Error scanning repository '%s': %s", scanned_repo.get("name", "Unknown"), scanned_repo["error"])
        return {"name": scanned_repo.get("name", "Unknown"), "markdown": f"Error scanning repository: {scanned_repo['error']}", "input_tokens": 0, "output_tokens": 0}
       
    name = scanned_repo.get("name")

    languages = scanned_repo.get("languages")
    language_str = ''
    for lang, count in languages.items():
        language_str += f"- {lang}: {count} files\n"

    top_level_modules = list_to_string(scanned_repo.get("top_level_modules"))
    signal_files = list_to_string(scanned_repo.get("signal_files"))
    file_tree = list_to_string(scanned_repo.get("file_tree"))
    dependencies = list_to_string(scanned_repo.get("dependencies"))
    readme = scanned_repo.get("readme")
    commit_messages = list_to_string(scanned_repo.get("commit_messages"))

    prompt = f"""
    You are helping a developer recall one of their own projects after being away from it for a while.

    Fill out the following note template for the repository "{name}". Write in first person as if the developer is writing notes to their future self. Be concise — this is a personal recall aid, not documentation for others. Only include information you can confidently infer from the provided data; do not invent details.

    ## Repository data

    **Languages:**
    {language_str}
    **Top-level modules:**
    {top_level_modules}

    **Signal files (infra/tooling present):**
    {signal_files}

    **Dependency files found:**
    {dependencies}

    **File tree:**
    {file_tree}

    **README:**
    {readme or "No README found."}

    **Commit history (most recent first):**
    {commit_messages}

    ## Note template to fill out

    {template}
    """

    # response = client.messages.count_tokens(
    #   model="claude-haiku-4-5",
    #   messages=[{"role": "user", "content": prompt}]
    # )


    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=2048,
        messages=[{"role": "user", "content": prompt}]
    )
    doc = {}
    doc["name"] = name
    doc["markdown"] = response.content[0].text
    doc["input_tokens"] = response.usage.input_tokens
    doc["output_tokens"] = response.usage.output_tokens
    # print("Number of input tokens:", response.input_tokens)
    # print("Number of output tokens:", response.output_tokens)
    # print("Total tokens:", response.total_tokens)
    # print("Generated note:")
    # print(response.choices[0].message.content)
    return doc

