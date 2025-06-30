# Entry point
import sys

# Core CLI functions
from logs.loader import load_logs
from reports.report_generator import generate_report
from utils.analyzer import (
    classify_user_agents,
    get_top_ips,
    get_top_urls,
    get_status_distribution,
    group_by_hour,
    group_by_day,
)

# Optional Flask App
from app import create_app


def run_cli():
    logs = load_logs("logs/sample.log")

    top_ips = get_top_ips(logs)
    top_urls = get_top_urls(logs)
    status_distribution = get_status_distribution(logs)
    hour_counts = group_by_hour(logs)
    day_counts = group_by_day(logs)
    user_agent_classes = classify_user_agents(logs)

    generate_report(
        top_ips,
        top_urls,
        status_distribution,
        hour_counts,
        day_counts,
        user_agent_classes,
    )


if __name__ == "__main__":
    # Usage:
    # python main.py           → CLI mode
    # python main.py web       → Start Flask dashboard

    if len(sys.argv) > 1 and sys.argv[1] == "web":
        app = create_app()
        app.run(debug=True)
    else:
        run_cli()
