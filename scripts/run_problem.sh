#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -ne 1 ]; then
  echo "usage: bash scripts/run_problem.sh <problem-path>"
  exit 1
fi

PROBLEM_PATH="$1"

docker build -f docker/base.Dockerfile -t python-assignment .
docker run --rm -it -v "$(pwd)/${PROBLEM_PATH}:/workspace" python-assignment
