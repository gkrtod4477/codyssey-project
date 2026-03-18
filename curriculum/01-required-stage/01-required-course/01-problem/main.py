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

    reverse_logs = sorted(
        logs,
        key=lambda row: datetime.strptime(row["timestamp"], "%Y-%m-%d %H:%M:%S"),
        reverse=True,
    )

    print_logs("=== 로그 출력: 과거 -> 현재 ===", logs)
    print_logs(
        "=== 로그 출력: 현재 -> 과거 ===",
        reverse_logs,
    )


if __name__ == "__main__":
    main()
