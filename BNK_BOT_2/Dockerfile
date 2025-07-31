FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY prod_report_bot1.py .
CMD ["python", "/app/prod_report_bot1.py"]
