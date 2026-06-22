FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
ENV STOCK_AGENT_MODE=demo PYTHONUNBUFFERED=1
CMD ["python", "langchain_merrary.py", "--stock-code", "600519"]

