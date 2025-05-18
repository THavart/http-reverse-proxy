FROM python:3.9-slim

WORKDIR /app

# Copy your Python files
COPY proxy_logger.py .
COPY proxy_server.py .
COPY proxy_router.py .

# Create logs directory
RUN mkdir -p audit_logs

# Expose proxy port
EXPOSE 8000

# Run the proxy server
CMD ["python", "proxy_server.py"]