# Log reader/parser
import re
from typing import List, Dict

LOG_PATTERN = re.compile(
    r"(?P<ip>\d+\.\d+\.\d+\.\d+)\s-\s-\s"               # IP Address
    r"\[(?P<datetime>[^\]]+)\]\s"                       # Date and time
    r'"(?P<method>\w+)\s(?P<url>\S+)\sHTTP/\d\.\d"\s'   # Method + URL + HTTP version
    r"(?P<status>\d{3})\s(?P<size>\d+|-)\s"             # Status + Size
    r'"(?P<referrer>[^"]*)"\s"(?P<user_agent>[^"]*)"'   # Referrer + User Agent
)

def parse_log_line(line: str) -> Dict:
    match = LOG_PATTERN.match(line)
    if match:
        return match.groupdict()
    return {}

def load_logs(filepath: str) -> List[Dict]:
    parsed_logs = []
    with open(filepath, 'r', encoding='utf-8') as file:
        for line in file:
            parsed = parse_log_line(line)
            if parsed:
                parsed_logs.append(parsed)
    return parsed_logs
