from flask import Blueprint, render_template, request, abort
from utils.analyzer import group_by_hour, group_by_day, get_status_distribution
from logs.loader import load_logs
from app.graph_utils import plot_hourly_requests, plot_daily_requests, plot_status_codes
import os

bp = Blueprint("dashboard", __name__)


@bp.route("/", methods=["GET"])
def dashboard():
    log_dir = "logs"

    # Check if log directory exists
    if not os.path.exists(log_dir):
        return render_template(
            "dashboard.html",
            log_files=[],
            selected_file=None,
            error="Log directory not found",
        )

    # Get all log files
    log_files = [f for f in os.listdir(log_dir) if f.endswith(".log")]

    # Handle case where no log files exist
    if not log_files:
        return render_template(
            "dashboard.html",
            log_files=[],
            selected_file=None,
            error="No log files found",
        )

    # Get selected file with validation
    selected_file = request.args.get("log", log_files[0])

    # Validate that selected file exists in the log_files list (security)
    if selected_file not in log_files:
        selected_file = log_files[0]

    # Load and process logs
    try:
        logs = load_logs(os.path.join(log_dir, selected_file))

        # Initialize charts as None
        hourly_chart = daily_chart = status_chart = None

        # Only generate charts if we have log data
        if logs:
            # Analytics
            hourly_data = group_by_hour(logs)
            daily_data = group_by_day(logs)
            status_data = get_status_distribution(logs)

            hourly_chart = plot_hourly_requests(hourly_data)
            daily_chart = plot_daily_requests(daily_data)
            status_chart = plot_status_codes(status_data)

    except Exception as e:
        return render_template(
            "dashboard.html",
            log_files=log_files,
            selected_file=selected_file,
            error=f"Error processing log file: {str(e)}",
        )

    return render_template(
        "dashboard.html",
        log_files=log_files,
        selected_file=selected_file,
        hourly_chart=hourly_chart,
        daily_chart=daily_chart,
        status_chart=status_chart,
    )
