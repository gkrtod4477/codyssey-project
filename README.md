# Python Assignment Project

## Folder structure

```text
curriculum/
  01-required-stage/
    01-required-course/
      01-problem/
        provided-files/
        artifacts/
```

## Rule

- One problem lives in one folder.
- Each problem folder must contain `main.py`.
- Put assignment-provided files in `provided-files/`.
- Put assignment outputs in `artifacts/`.
- Docker runs one problem folder at a time.

## Run

```bash
bash scripts/run_problem.sh curriculum/01-required-stage/01-required-course/01-problem
```

## Local Run

PyQt5 과제처럼 GUI가 필요한 문제는 Docker 대신 로컬에서 직접 실행하는 편이 안전합니다.

```bash
cd /Users/admin/Desktop/study/codyssey/python-project
python3 -m pip install PyQt5==5.15.11
python3 curriculum/01-required-stage/02-required-course/03-problem/main.py
```

직접 실행 파일을 지정하려면 아래 명령도 사용할 수 있습니다.

```bash
python3 curriculum/01-required-stage/02-required-course/03-problem/calculator.py
```
