# Entry point
import sys
import os

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


def run_cli(log_path=None):
    # Prompt for log file path if not provided
    if not log_path:
        log_path = input("Enter the path to your .log file: ").strip()

    # Validate file
    if not os.path.isfile(log_path):
        print(f"❌ Error: File '{log_path}' does not exist.")
        return

    if not log_path.lower().endswith(".log"):
        print("❌ Error: Only .log files are supported.")
        return

    # Load and analyze logs
    logs = load_logs(log_path)

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
        log_filename=log_path,  # Pass the log file path
    )


if __name__ == "__main__":
    # Usage:
    # python main.py              → CLI with prompt
    # python main.py logs/file.log → CLI with file argument
    # python main.py web          → Start Flask dashboard

    if len(sys.argv) > 1:
        if sys.argv[1] == "web":
            app = create_app()
            app.run(debug=True)
        else:
            run_cli(sys.argv[1])
    else:
        run_cli()
