# Data aggregation logic
from collections import Counter, defaultdict
from datetime import datetime
from typing import List, Dict

def get_top_ips(logs: List[Dict], top_n: int = 5):
    ip_counter = Counter(log['ip'] for log in logs)
    return ip_counter.most_common(top_n)

def get_top_urls(logs: List[Dict], top_n: int = 5):
    url_counter = Counter(log['url'] for log in logs)
    return url_counter.most_common(top_n)

def get_status_distribution(logs: List[Dict]):
    status_counter = Counter(log['status'] for log in logs)
    return dict(status_counter)

def group_by_hour(logs):
    hour_counts = defaultdict(int)
    for log in logs:
        dt = parse_datetime(log['datetime'])
        hour_str = dt.strftime("%Y-%m-%d %H:00")
        hour_counts[hour_str] += 1
    return dict(hour_counts)

def group_by_day(logs):
    day_counts = defaultdict(int)
    for log in logs:
        dt = parse_datetime(log['datetime'])
        day_str = dt.strftime("%Y-%m-%d")
        day_counts[day_str] += 1
    return dict(day_counts)

def parse_datetime(dt_str):
    return datetime.strptime(dt_str.split(" ")[0], "%d/%b/%Y:%H:%M:%S")
