FROM python:3.10-slim

ARG DEBIAN_FRONTEND=noninteractive
ENV TZ=Asia/Shanghai

RUN apt-get update && \
    apt-get install vim wget curl build-essential libssl-dev  -y && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

RUN pip3 install --upgrade pip && pip3 install playwright
RUN playwright install
RUN playwright install-deps

# Install Python dependencies
COPY requirements.txt requirements.txt

RUN pip3 install -r requirements.txt && rm -rf /root/.cache/pip

COPY . .

EXPOSE 8891

# Run the app
CMD ["python", "main.py"]
