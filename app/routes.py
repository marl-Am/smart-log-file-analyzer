from flask import Blueprint, render_template, request, abort
from utils.analyzer import group_by_hour, group_by_day, get_status_distribution
from logs.loader import load_logs
from app.graph_utils import plot_hourly_requests, plot_daily_requests, plot_status_codes
import os

bp = Blueprint("dashboard", __name__)


def filter_logs(logs, method_filter=None, status_filter=None):
    """Filter logs by HTTP method and/or status code"""
    if not logs:
        return logs

    filtered_logs = logs

    # Filter by HTTP method
    if method_filter and method_filter != "all":
        filtered_logs = [
            log for log in filtered_logs if log.get("method") == method_filter
        ]

    # Filter by status code
    if status_filter and status_filter != "all":
        # Debug: Print some information to help diagnose the issue
        print(f"DEBUG: status_filter = {status_filter} (type: {type(status_filter)})")
        if filtered_logs:
            sample_log = filtered_logs[0]
            print(
                f"DEBUG: Sample log status = {sample_log.get('status')} (type: {type(sample_log.get('status'))})"
            )

        # Try both string and integer comparison
        filtered_logs = [
            log
            for log in filtered_logs
            if (
                str(log.get("status")) == status_filter  # String comparison
                or log.get("status") == status_filter  # Direct comparison
                or (
                    status_filter.isdigit() and log.get("status") == int(status_filter)
                )  # Integer comparison
            )
        ]

        print(f"DEBUG: After filtering, {len(filtered_logs)} logs remain")

    return filtered_logs


def get_available_methods(logs):
    """Get all unique HTTP methods from logs"""
    if not logs:
        return []
    methods = set(log.get("method") for log in logs if log.get("method"))
    return sorted(list(methods))


def get_available_status_codes(logs):
    """Get all unique status codes from logs"""
    if not logs:
        return []
    status_codes = set(log.get("status") for log in logs if log.get("status"))
    # Debug: Print status codes and their types
    print(f"DEBUG: Available status codes: {status_codes}")
    for code in list(status_codes)[:3]:  # Print first 3 for debugging
        print(f"DEBUG: Status code {code} has type {type(code)}")
    return sorted(list(status_codes))


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

    # Get filter parameters
    method_filter = request.args.get("method", "all")
    status_filter = request.args.get("status", "all")

    # Load and process logs
    try:
        logs = load_logs(os.path.join(log_dir, selected_file))

        # Get available filter options from all logs
        available_methods = get_available_methods(logs)
        available_status_codes = get_available_status_codes(logs)

        # Apply filters
        filtered_logs = filter_logs(logs, method_filter, status_filter)

        # Initialize charts as None
        hourly_chart = daily_chart = status_chart = None

        # Only generate charts if we have log data
        if filtered_logs:
            # Analytics on filtered data
            hourly_data = group_by_hour(filtered_logs)
            daily_data = group_by_day(filtered_logs)
            status_data = get_status_distribution(filtered_logs)

            hourly_chart = plot_hourly_requests(hourly_data)
            daily_chart = plot_daily_requests(daily_data)
            status_chart = plot_status_codes(status_data)

        # Calculate filter stats
        total_logs = len(logs) if logs else 0
        filtered_count = len(filtered_logs) if filtered_logs else 0

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
        # Filter options
        available_methods=available_methods,
        available_status_codes=available_status_codes,
        selected_method=method_filter,
        selected_status=status_filter,
        # Stats
        total_logs=total_logs,
        filtered_count=filtered_count,
    )
