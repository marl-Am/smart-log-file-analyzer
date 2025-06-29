# Output formatter

from datetime import datetime
import os
from typing import Dict, List, Tuple


def format_section(title: str, items: List[Tuple[str, int]]) -> str:
    lines = [f"### {title}"]
    for key, value in items:
        lines.append(f"- `{key}`: **{value}**")
    return "\n".join(lines)


def format_status_section(status_counts: Dict[str, int]) -> str:
    lines = ["### Status Code Distribution"]
    for status, count in status_counts.items():
        lines.append(f"- `{status}`: **{count}**")
    return "\n".join(lines)


def generate_report(
    top_ips: List[Tuple[str, int]],
    top_urls: List[Tuple[str, int]],
    status_distribution: Dict[str, int],
    to_file: bool = True,
):
    now = datetime.now()
    timestamp = now.strftime("%Y-%m-%d %H:%M:%S")
    header = f"# smart Log Analyzer Report\nGenerated on: `{timestamp}`\n\n"
    body = "\n\n".join(
        [
            format_section("Top IPs", top_ips),
            format_section("Top URLs", top_urls),
            format_status_section(status_distribution),
        ]
    )

    report = header + body
    print(report)
    # Save to root-level /reports/ folder
    if to_file:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        reports_dir = os.path.join(base_dir, "reports")
        os.makedirs(reports_dir, exist_ok=True)
        filename = os.path.join(reports_dir, f"report_{now.strftime('%Y%m%d_%H%M%S')}.md")

        with open(filename, "w", encoding="utf-8") as f:
            f.write(report)

        print(f"\n✅ Report saved to `{filename}`")
