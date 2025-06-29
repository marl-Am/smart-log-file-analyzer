# Data aggregation logic
from collections import Counter
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