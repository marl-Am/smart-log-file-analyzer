# Entry point
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


if __name__ == "__main__":
    logs = load_logs("logs/sample.log")
    # Testing logs/loader.py
    # for entry in logs[:5]:
    #     print(entry)

    # Testing utils/analyzer.py
    # print("\n\nTop IPs:")
    # for ip, count in get_top_ips(logs):
    #     print(f"{ip}: {count} requests")

    # print("\n\nTop URLs:")
    # for url, count in get_top_urls(logs):
    #     print(f"{url}: {count} hits")

    # print("\n\nStatus Code Distribution:")
    # for status, count in get_status_distribution(logs).items():
    #     print(f"{status}: {count}")

    top_ips = get_top_ips(logs)
    top_urls = get_top_urls(logs)
    status_distribution = get_status_distribution(logs)

    # generate_report(top_ips, top_urls, status_distribution)

    # after loading logs
    hour_counts = group_by_hour(logs)
    day_counts = group_by_day(logs)

    # print("\nRequests per Hour:")
    # for hour in sorted(hour_counts):
    #     print(f"{hour}: {hour_counts[hour]}")

    # print("\nRequests per Day:")
    # for day in sorted(day_counts):
    #     print(f"{day}: {day_counts[day]}")

    user_agent_classes = classify_user_agents(logs)

    # print("\nTop Bots:")
    # for agent, count in sorted(user_agent_classes["bots"].items(), key=lambda x: -x[1])[:5]:
    #     print(f"- {agent}:  {count}")

    # print("\nTop Browsers:")
    # for agent, count in sorted(user_agent_classes["browsers"].items(), key=lambda x: -x[1])[:5]:
    #     print(f"- {agent}: {count}")

    # print("\nUnknown User-Agents:")
    # for agent, count in sorted(user_agent_classes["unknown"].items(), key=lambda x: -x[1])[:5]:
    #     print(f"- {agent}: {count}")

    generate_report(
        top_ips,
        top_urls,
        status_distribution,
        hour_counts,
        day_counts,
        user_agent_classes,
    )
