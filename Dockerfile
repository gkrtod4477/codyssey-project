FROM python:3.12-slim

WORKDIR /workspace

COPY requirements.txt /tmp/requirements.txt
RUN if [ -s /tmp/requirements.txt ]; then pip install --no-cache-dir -r /tmp/requirements.txt; fi

CMD ["python", "main.py"]
