from flask import Blueprint, render_template, request, abort
from utils.analyzer import (
    group_by_hour,
    group_by_day,
    get_status_distribution,
    classify_user_agents,
    get_top_ips,
    get_top_urls,
)
from logs.loader import load_logs
from app.graph_utils import plot_hourly_requests, plot_daily_requests, plot_status_codes
from reports.report_generator import generate_report
from utils.md_renderer import render_markdown_report
import os
import tempfile
from datetime import datetime, date

bp = Blueprint("dashboard", __name__)


def parse_log_timestamp(log_entry):
    """
    Parse timestamp from log entry. Handles Apache/Nginx log format.
    """
    # For Apache/Nginx logs, the timestamp is usually in the raw log line
    # Format: [15/Jan/2025:14:30:45 +0200]

    timestamp_field = (
        log_entry.get("timestamp") or log_entry.get("time") or log_entry.get("date")
    )

    if not timestamp_field:
        # If no parsed timestamp field, try to extract from raw log line
        raw_line = log_entry.get("raw_line", "")
        if raw_line:
            # Look for timestamp pattern in brackets
            import re

            timestamp_pattern = r"\[(\d{2}/\w{3}/\d{4}:\d{2}:\d{2}:\d{2})\s*[+-]\d{4}\]"
            match = re.search(timestamp_pattern, raw_line)
            if match:
                timestamp_field = match.group(1)

    if not timestamp_field:
        return None

    # If it's already a datetime object
    if isinstance(timestamp_field, datetime):
        return timestamp_field.date()

    # If it's a string, try to parse common formats
    if isinstance(timestamp_field, str):
        # Common log timestamp formats
        formats = [
            "%d/%b/%Y:%H:%M:%S",  # 15/Jan/2025:14:30:45 (Apache format)
            "%Y-%m-%d %H:%M:%S",  # 2025-01-15 14:30:45
            "%Y-%m-%d",  # 2025-01-15
            "%d/%m/%Y",  # 15/01/2025
            "%m/%d/%Y",  # 01/15/2025
        ]

        for fmt in formats:
            try:
                return datetime.strptime(timestamp_field, fmt).date()
            except ValueError:
                continue

    return None


def filter_logs(
    logs, method_filter=None, status_filter=None, start_date=None, end_date=None
):
    """Filter logs by HTTP method, status code, and date range"""
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
        filtered_logs = [
            log
            for log in filtered_logs
            if (
                str(log.get("status")) == status_filter
                or log.get("status") == status_filter
                or (status_filter.isdigit() and log.get("status") == int(status_filter))
            )
        ]

    # Filter by date range
    if start_date or end_date:
        date_filtered_logs = []

        for log in filtered_logs:
            log_date = parse_log_timestamp(log)

            if log_date is None:
                continue  # Skip logs without valid timestamps

            # Check if log date is within range
            if start_date and log_date < start_date:
                continue
            if end_date and log_date > end_date:
                continue

            date_filtered_logs.append(log)

        filtered_logs = date_filtered_logs

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
    return sorted(list(status_codes))


def get_date_range_info(logs, start_date, end_date):
    """Get information about the date range of logs"""
    if not logs:
        return None

    # Get actual date range of logs
    log_dates = []
    for log in logs:
        log_date = parse_log_timestamp(log)
        if log_date:
            log_dates.append(log_date)

    if not log_dates:
        return "No valid timestamps found in logs"

    actual_start = min(log_dates)
    actual_end = max(log_dates)

    info_parts = []

    if start_date or end_date:
        filter_start = start_date or actual_start
        filter_end = end_date or actual_end
        info_parts.append(f"Filtered: {filter_start} to {filter_end}")

    info_parts.append(f"Available data: {actual_start} to {actual_end}")

    return " | ".join(info_parts)


def generate_markdown_report(logs, log_filename):
    """Generate markdown report from logs and return rendered HTML"""
    if not logs:
        return None

    try:
        # Get all the analytics data
        top_ips = get_top_ips(logs)
        top_urls = get_top_urls(logs)
        status_distribution = get_status_distribution(logs)
        hour_counts = group_by_hour(logs)
        day_counts = group_by_day(logs)
        user_agent_classes = classify_user_agents(logs)

        # Create a temporary file to store the markdown report
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".md", delete=False
        ) as temp_file:
            temp_filename = temp_file.name

            # Generate the report content without saving to the reports directory
            from reports.report_generator import (
                format_section,
                format_status_section,
                format_time_series,
                format_user_agents,
            )

            now = datetime.now()
            timestamp = now.strftime("%Y-%m-%d %H:%M:%S")

            # Create header with log filename
            log_info = f" - {os.path.basename(log_filename)}" if log_filename else ""
            header = f"# Log Analyzer Report{log_info}\nGenerated on: `{timestamp}`\n\n"

            body = "\n\n".join(
                [
                    format_section("Top IPs", top_ips),
                    format_section("Top URLs", top_urls),
                    format_status_section(status_distribution),
                    format_time_series("Hourly Request Volume", hour_counts),
                    format_time_series("Daily Request Volume", day_counts),
                    format_user_agents("Top Bots", user_agent_classes.get("bots", {})),
                    format_user_agents(
                        "Top Browsers", user_agent_classes.get("browsers", {})
                    ),
                    format_user_agents(
                        "Unknown Agents", user_agent_classes.get("unknown", {})
                    ),
                ]
            )

            report_content = header + body
            temp_file.write(report_content)

        # Render the markdown to HTML
        html_content = render_markdown_report(temp_filename)

        # Clean up the temporary file
        os.unlink(temp_filename)

        return html_content

    except Exception as e:
        print(f"Error generating markdown report: {e}")
        return None


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

    # Parse date parameters
    start_date_str = request.args.get("start_date")
    end_date_str = request.args.get("end_date")

    start_date = None
    end_date = None

    if start_date_str:
        try:
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
        except ValueError:
            pass  # Invalid date format, ignore

    if end_date_str:
        try:
            end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
        except ValueError:
            pass  # Invalid date format, ignore

    # Load and process logs
    try:
        logs = load_logs(os.path.join(log_dir, selected_file))

        # Get available filter options from all logs
        available_methods = get_available_methods(logs)
        available_status_codes = get_available_status_codes(logs)

        # Apply filters
        filtered_logs = filter_logs(
            logs, method_filter, status_filter, start_date, end_date
        )

        # Get date range information
        date_range_info = get_date_range_info(filtered_logs, start_date, end_date)

        # Initialize charts as None
        hourly_chart = daily_chart = status_chart = None
        report_html = None

        # Only generate charts if we have log data
        if filtered_logs:
            # Analytics on filtered data
            hourly_data = group_by_hour(filtered_logs)
            daily_data = group_by_day(filtered_logs)
            status_data = get_status_distribution(filtered_logs)

            hourly_chart = plot_hourly_requests(hourly_data)
            daily_chart = plot_daily_requests(daily_data)
            status_chart = plot_status_codes(status_data)

            # Generate markdown report
            report_html = generate_markdown_report(filtered_logs, selected_file)

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
        # Date filter values
        start_date=start_date_str,
        end_date=end_date_str,
        date_range_info=date_range_info,
        # Stats
        total_logs=total_logs,
        filtered_count=filtered_count,
        # Markdown report
        report_html=report_html,
    )
