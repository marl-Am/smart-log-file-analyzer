# Entry point
from logs.loader import load_logs

if __name__ == "__main__":
    logs = load_logs("logs/sample.log")
    # Print out 5 lines
    for entry in logs[:5]:
        print(entry)