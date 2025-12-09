FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app/ai_service

ENV PYTHONPATH=/app
EXPOSE 8003

CMD ["uvicorn", "ai_service.main:app", "--host", "0.0.0.0", "--port", "8003"]

