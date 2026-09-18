FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY server.py file_search.py .
COPY docs ./docs

CMD ["python", "server.py"]
