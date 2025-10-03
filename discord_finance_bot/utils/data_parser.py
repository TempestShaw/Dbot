from typing import List, Dict


def to_markdown_table(items: List[Dict], headers: List[str]) -> str:
    """Convert a list of dicts to a markdown table with given headers."""
    if not items:
        return "No data."

    line = "| " + " | ".join(headers) + " |"
    sep = "| " + " | ".join(["---"] * len(headers)) + " |"
    rows = [line, sep]
    for obj in items:
        rows.append("| " + " | ".join([str(obj.get(h, "")) for h in headers]) + " |")
    return "\n".join(rows)