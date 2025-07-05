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


def format_time_series(title: str, data: Dict[str, int]) -> str:
    lines = [f"### {title}"]
    for key in sorted(data):
        lines.append(f"- `{key}`: **{data[key]}**")
    return "\n".join(lines)


def format_user_agents(title: str, data: Dict[str, int]) -> str:
    lines = [f"### {title}"]
    top_agents = sorted(data.items(), key=lambda x: -x[1])[:5]
    for agent, count in top_agents:
        lines.append(
            f"- `{agent[:80]}...`: **{count}**"
            if len(agent) > 80
            else f"- `{agent}`: **{count}**"
        )
    return "\n".join(lines)


def generate_report(
    top_ips: List[Tuple[str, int]],
    top_urls: List[Tuple[str, int]],
    status_distribution: Dict[str, int],
    hour_counts: Dict[str, int],
    day_counts: Dict[str, int],
    user_agent_classes: Dict[str, int],
    log_filename: str = None,
    to_file: bool = True,
):
    now = datetime.now()
    timestamp = now.strftime("%Y-%m-%d %H:%M:%S")

    # Create header with log filename if provided
    log_info = f" - {log_filename}" if log_filename else ""
    header = f"# Log Analyzer Report{log_info}\nGenerated on: `{timestamp}`\n\n"

    body = "\n\n".join(
        [
            format_section("Top IPs", top_ips),
            format_section("Top URLs", top_urls),
            format_status_section(status_distribution),
            format_time_series("Hourly Request Volume", hour_counts),
            format_time_series("Daily Request Volume", day_counts),
            format_user_agents("Top Bots", user_agent_classes["bots"]),
            format_user_agents("Top Browsers", user_agent_classes["browsers"]),
            format_user_agents("Unknown Agents", user_agent_classes["unknown"]),
        ]
    )

    report = header + body

    # Save to root-level /reports/ folder
    if to_file:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        reports_dir = os.path.join(base_dir, "reports")
        os.makedirs(reports_dir, exist_ok=True)

        # Generate filename based on log file name if provided
        if log_filename:
            # Extract base name without extension and path
            log_base = os.path.splitext(os.path.basename(log_filename))[0]
            filename = os.path.join(
                reports_dir, f"report_{log_base}_{now.strftime('%Y%m%d_%H%M%S')}.md"
            )
        else:
            filename = os.path.join(
                reports_dir, f"report_{now.strftime('%Y%m%d_%H%M%S')}.md"
            )

        with open(filename, "w", encoding="utf-8") as f:
            f.write(report)

        print(f"\n✅ Report saved to `{filename}`")
        return filename  # Return the filename for potential use by md_renderer
