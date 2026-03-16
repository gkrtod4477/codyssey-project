from pathlib import Path


def main():
    problem_dir = Path(__file__).resolve().parent
    log_file = problem_dir / "provided-files" / "logs" / "mission_computer_main.log"

    print(log_file.read_text(encoding="utf-8"), end="")


if __name__ == "__main__":
    main()
