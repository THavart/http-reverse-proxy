FROM python:3.9-slim

WORKDIR /app

# Install Redis client library
RUN pip install redis

# Copy your Python files
COPY proxy_logger.py .
COPY proxy_server.py .

# Create logs directory
RUN mkdir -p proxy_logs

# Expose proxy port
EXPOSE 8000

# Run the proxy server
CMD ["python", "proxy_server.py"]