FROM python:3.10-slim

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && \
    apt-get install -y nmap cron pciutils dmidecode && \
    apt-get clean

WORKDIR /app

# BACKEND FILES
COPY scanner_backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY scanner_backend/scanner.py .
COPY scanner_backend/drivers_scanner.py .
COPY scanner_backend/server.py .
COPY scanner_backend/run.sh .
COPY scanner_backend/start.sh .

# CRON FILES
COPY scanner_server/crontab.txt /etc/cron.d/cve-cron
COPY scanner_server/run.sh /app/server_run.sh

RUN chmod +x /app/run.sh && \
    chmod +x /app/start.sh && \
    chmod +x /app/server_run.sh && \
    chmod 0644 /etc/cron.d/cve-cron

RUN mkdir -p /app/output
RUN crontab /etc/cron.d/cve-cron

EXPOSE 5000
ENTRYPOINT ["/app/start.sh"]

