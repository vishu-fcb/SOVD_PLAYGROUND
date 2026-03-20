FROM python:3.12-slim
WORKDIR /app
COPY . .
RUN pip install --no-cache-dir -r requirements.txt
# Default port; can be overridden by CMD in compose
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]