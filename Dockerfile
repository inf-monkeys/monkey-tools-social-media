FROM python:3.10-slim

ARG DEBIAN_FRONTEND=noninteractive
ENV TZ=Asia/Shanghai

RUN apt-get update && \
    apt-get install vim wget curl build-essential  -y && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies
COPY requirements.txt requirements.txt

RUN pip3 install -r requirements.txt && rm -rf /root/.cache/pip

RUN playwright install
RUN playwright install-deps

COPY . .

EXPOSE 8891

# Run the app
CMD ["python", "main.py"]
