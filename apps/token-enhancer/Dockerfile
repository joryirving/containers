# syntax=docker/dockerfile:1

ARG VERSION

FROM docker.io/library/python:3.12-slim

WORKDIR /app

# Clone upstream repo
RUN git clone --depth 1 https://github.com/Boof-Pack/token-enhancer.git /src

WORKDIR /src

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose port
EXPOSE 8080

# Run the proxy server
CMD ["python3", "proxy.py"]
