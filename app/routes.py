from flask import Blueprint, render_template
from utils.analyzer import group_by_hour, group_by_day, get_status_distribution
from logs.loader import load_logs
from app.graph_utils import plot_hourly_requests, plot_daily_requests, plot_status_codes

bp = Blueprint("dashboard", __name__)


@bp.route("/")
def dashboard():
    logs = load_logs("logs/sample.log")
    hourly_data = group_by_hour(logs)
    daily_data = group_by_day(logs)
    status_data = get_status_distribution(logs)

    hourly_chart = plot_hourly_requests(hourly_data)
    daily_chart = plot_daily_requests(daily_data)
    status_chart = plot_status_codes(status_data)

    return render_template(
        "dashboard.html", hourly_chart=hourly_chart, daily_chart=daily_chart, status_chart=status_chart
    )
