# Entry point
from logs.loader import load_logs
from utils.analyzer import get_top_ips, get_top_urls, get_status_distribution

if __name__ == "__main__":
    logs = load_logs("logs/sample.log")
    # Testing logs/loader.py
    # for entry in logs[:5]:
    #     print(entry)

    # Testing utils/analyzer.py
    print("\n\nTop IPs:")
    for ip, count in get_top_ips(logs):
        print(f"{ip}: {count} requests")

    print("\n\nTop URLs:")
    for url, count in get_top_urls(logs):
        print(f"{url}: {count} hits")

    print("\n\nStatus Code Distribution:")
    for status, count in get_status_distribution(logs).items():
        print(f"{status}: {count}")
