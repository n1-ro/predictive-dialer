# Python service image (lead sync daemon)
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY astguiclient/ ./astguiclient/
CMD ["python", "-m", "astguiclient.lead_sync"]
