from pathlib import Path
import csv
from datetime import datetime


def print_logs(title, logs):
    print(title)
    print("timestamp,event,message")
    for log in logs:
        print(f'{log["timestamp"]},{log["event"]},{log["message"]}')
    print()


def main():
    problem_dir = Path(__file__).resolve().parent
    log_file = problem_dir / "provided-files" / "logs" / "mission_computer_main.log"

    with log_file.open(encoding="utf-8", newline="") as file:
        logs = list(csv.DictReader(file))

    def timestamp_key(row):
        return datetime.strptime(row["timestamp"], "%Y-%m-%d %H:%M:%S")

    chronological_logs = logs.copy()
    chronological_logs.sort(key=timestamp_key)

    reverse_logs = logs.copy()
    reverse_logs.sort(key=timestamp_key, reverse=True)

    print_logs("=== 로그 출력: 과거 -> 현재 ===", chronological_logs)
    print_logs(
        "=== 로그 출력: 현재 -> 과거 ===",
        reverse_logs,
    )


if __name__ == "__main__":
    main()
