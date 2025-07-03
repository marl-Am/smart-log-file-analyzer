# Log Generator Script Generates realistic Apache/Nginx access logs for testing log analysis tools.
# Creates a large log file with varied realistic data
import random
import datetime
import os
from typing import List


class LogGenerator:
    def __init__(self):
        # Realistic IP address ranges (mix of real and private)
        self.ip_ranges = [
            "66.249.76.",  # Google crawler
            "40.77.167.",  # Bing crawler
            "157.55.39.",  # Microsoft
            "192.168.1.",  # Internal network
            "10.0.0.",  # Internal network
            "203.0.113.",  # Documentation IP
            "198.51.100.",  # Documentation IP
            "185.199.108.",  # GitHub
            "151.101.193.",  # Reddit/Fastly
            "172.217.14.",  # Google services
        ]

        # Common HTTP methods and their weights
        self.http_methods = [
            ("GET", 80),
            ("POST", 15),
            ("PUT", 2),
            ("DELETE", 1),
            ("HEAD", 2),
        ]

        # Realistic URL paths with weights
        self.url_paths = [
            ("/", 20),
            ("/index.html", 15),
            ("/about", 8),
            ("/contact", 5),
            ("/api/users", 10),
            ("/api/data", 12),
            ("/login", 6),
            ("/dashboard", 8),
            ("/products", 7),
            ("/favicon.ico", 15),
            ("/robots.txt", 3),
            ("/sitemap.xml", 2),
            ("/2025/01/14/new-year-updates/", 1),
            ("/2025/02/15/machine-learning-tutorial/", 1),
            ("/2025/03/20/web-development-best-practices/", 1),
            ("/assets/css/style.css", 5),
            ("/assets/js/main.js", 4),
            ("/images/logo.png", 3),
            ("/admin/login", 1),
            ("/wp-admin/", 1),  # Apparently common attack target
        ]

        # HTTP status codes with realistic distribution
        self.status_codes = [
            (200, 70),  # OK
            (404, 15),  # Not Found
            (301, 5),  # Moved Permanently
            (302, 3),  # Found
            (403, 2),  # Forbidden
            (500, 2),  # Internal Server Error
            (304, 2),  # Not Modified
            (401, 1),  # Unauthorized
        ]

        # Realistic User Agents
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
            "Mozilla/5.0 (Linux; Android 6.0.1; Nexus 5X Build/MMB29P) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.92 Mobile Safari/537.36 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)",
            "Mozilla/5.0 (compatible; bingbot/2.0; +http://www.bing.com/bingbot.htm)",
            "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Mobile/15E148 Safari/604.1",
            "Mozilla/5.0 (iPad; CPU OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Mobile/15E148 Safari/604.1",
            "Mozilla/5.0 (Linux; Android 10; SM-G981B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.120 Mobile Safari/537.36",
            "curl/7.68.0",
            "python-requests/2.25.1",
        ]

        # Common referrers
        self.referrers = [
            '"-"',
            '"https://www.google.com/"',
            '"https://www.bing.com/"',
            '"https://github.com/"',
            '"https://stackoverflow.com/"',
            '"https://reddit.com/"',
            '"https://twitter.com/"',
            '"https://facebook.com/"',
        ]
        pass

    def generate_filename(self, base_name: str = "sample") -> str:
        """Generate filename with current timestamp"""
        timestamp = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
        return f"{base_name}_{timestamp}.log"

    def get_date_range(self, num_days: int = None) -> tuple:
        """Get appropriate date range - from start of year to today"""
        today = datetime.datetime.now()

        if num_days:
            # If specific number of days requested, go back that many days
            start_date = today - datetime.timedelta(days=num_days - 1)
        else:
            # Default: from January 1st of current year to today
            start_date = datetime.datetime(today.year, 1, 1, 0, 0, 0)

        return start_date, today

    def generate_daily_distribution(self, total_lines: int, num_days: int) -> List[int]:
        """Generate realistic daily request distribution with weekday/weekend patterns"""
        base_daily = total_lines // num_days
        daily_requests = []

        for day in range(num_days):
            # Create realistic variations:
            # - Weekdays: 80-120% of base
            # - Weekends: 60-90% of base
            # - Random spikes: occasional 150-200% days

            day_of_week = day % 7
            is_weekend = day_of_week in [5, 6]  # Saturday, Sunday

            if random.random() < 0.1:  # 10% chance of spike day
                multiplier = random.uniform(1.5, 2.0)
            elif is_weekend:
                multiplier = random.uniform(0.6, 0.9)
            else:
                multiplier = random.uniform(0.8, 1.2)

            daily_count = int(base_daily * multiplier)
            daily_requests.append(daily_count)

        # Adjust to ensure total equals target
        current_total = sum(daily_requests)
        difference = total_lines - current_total

        # Distribute the difference randomly across days
        for _ in range(abs(difference)):
            day_idx = random.randint(0, num_days - 1)
            if difference > 0:
                daily_requests[day_idx] += 1
            else:
                if daily_requests[day_idx] > 0:
                    daily_requests[day_idx] -= 1

        return daily_requests

    def weighted_choice(self, choices: List[tuple]) -> str:
        """Select item based on weights"""
        total = sum(weight for _, weight in choices)
        r = random.uniform(0, total)
        upto = 0
        for choice, weight in choices:
            if upto + weight >= r:
                return choice
            upto += weight
        return choices[-1][0]

    def generate_ip(self) -> str:
        """Generate a realistic IP address"""
        base = random.choice(self.ip_ranges)
        return base + str(random.randint(1, 254))

    def generate_timestamp(self, base_date: datetime.datetime) -> str:
        """Generate timestamp in Apache log format"""
        # Add random seconds to base date
        random_seconds = random.randint(0, 86400)  # 0 to 24 hours
        timestamp = base_date + datetime.timedelta(seconds=random_seconds)
        return timestamp.strftime("[%d/%b/%Y:%H:%M:%S +0200]")

    def generate_request_line(self) -> tuple:
        """Generate HTTP request line and expected response size"""
        method = self.weighted_choice(self.http_methods)
        path = self.weighted_choice(self.url_paths)

        # Determine response size based on path and method
        if path in ["/favicon.ico", "/robots.txt"]:
            size = random.randint(100, 2000)
        elif path.endswith((".css", ".js")):
            size = random.randint(5000, 50000)
        elif path.endswith((".png", ".jpg", ".gif")):
            size = random.randint(10000, 200000)
        elif method == "POST":
            size = random.randint(500, 5000)
        else:
            size = random.randint(1000, 20000)

        return f'"{method} {path} HTTP/1.1"', size

    def generate_log_line(self, base_date: datetime.datetime) -> str:
        """Generate a complete log line"""
        ip = self.generate_ip()
        timestamp = self.generate_timestamp(base_date)
        request_line, expected_size = self.generate_request_line()
        status_code = self.weighted_choice(self.status_codes)

        # Adjust size based on status code
        if status_code in [404, 403, 401]:
            size = random.randint(200, 1000)
        else:
            size = expected_size

        referrer = random.choice(self.referrers)
        user_agent = f'"{random.choice(self.user_agents)}"'

        return f"{ip} - - {timestamp} {request_line} {status_code} {size} {referrer} {user_agent}"

    def generate_logs(self, num_lines: int, base_filename: str = "sample"):
        """Generate log file with specified number of lines"""
        print(f"Generating {num_lines:,} log lines...")

        # Create logs directory if it doesn't exist
        logs_dir = os.path.join("..", "logs")
        os.makedirs(logs_dir, exist_ok=True)

        # Generate timestamped filename
        output_file = self.generate_filename(base_filename)
        full_output_path = os.path.join(logs_dir, output_file)

        print(f"Output file: {output_file}")

        # Start from a base date and spread logs over several days
        base_date = datetime.datetime(2020, 9, 1, 0, 0, 0)

        # Generate realistic daily distributions
        num_days = 30
        daily_requests = self.generate_daily_distribution(num_lines, num_days)

        print(f"Distributing logs across {num_days} days...")
        print(
            f"Daily requests range: {min(daily_requests):,} - {max(daily_requests):,}"
        )

        with open(full_output_path, "w") as f:
            line_count = 0
            for day in range(num_days):
                current_date = base_date + datetime.timedelta(days=day)
                requests_today = daily_requests[day]

                for _ in range(requests_today):
                    log_line = self.generate_log_line(current_date)
                    f.write(log_line + "\n")
                    line_count += 1

                    # Progress indicator
                    if line_count % 10000 == 0:
                        print(f"Generated {line_count:,} lines...")

        # Calculate file size
        file_size = os.path.getsize(full_output_path)
        size_mb = file_size / (1024 * 1024)

        print(f"\nLog file generated successfully!")
        print(f"File: {full_output_path}")
        print(f"Lines: {line_count:,}")
        print(f"Size: {size_mb:.2f} MB")


def main():
    generator = LogGenerator()
    num_lines = 100000
    base_filename = "sample"

    print("Apache/Nginx Log Generator")
    print("=" * 30)

    # Option to customize number of lines
    try:
        user_input = (
            input(f"Generate {num_lines:,} lines? (y/n) or enter number: ")
            .strip()
            .lower()
        )
        if user_input == "n":
            return
        elif user_input != "y" and user_input != "":
            num_lines = int(user_input)
    except ValueError:
        print("Invalid input, using default...")

    # Option to customize base filename
    try:
        filename_input = input(f"Base filename (default: '{base_filename}'): ").strip()
        if filename_input:
            base_filename = filename_input
    except:
        print("Using default filename...")

    generator.generate_logs(num_lines, base_filename)

    print(f"\nTo generate larger files:")
    print(f"  Small test: 10,000 lines (~1.5 MB)")
    print(f"  Medium: 100,000 lines (~15 MB)")
    print(f"  Large: 1,000,000 lines (~150 MB)")
    print(f"  Very large: 10,000,000 lines (~1.5 GB)")
    print(f"\nFiles will be saved as: {base_filename}_YYYY_MM_DD_HH_MM_SS.log")


if __name__ == "__main__":
    main()
