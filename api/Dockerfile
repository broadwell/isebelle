# Some of the stuff we need doesn't work well on Alpine
#FROM python:3.12-slim
FROM nvidia/cuda:12.2.0-devel-ubuntu22.04
#FROM nvidia/cuda:12.2.0-runtime-ubuntu22.04
#FROM nvcr.io/nvidia/ai-workbench/python-cuda122:1.0.6

WORKDIR /app
EXPOSE 5000

# Container is used with live-reload so we don't want .pyc stored on bind-mounted host filesystem
ENV PYTHONPYCACHEPREFIX=/tmp
# Makes local modules easy to use from Jupyter
ENV PYTHONPATH=$PYTHONPATH:/app

# Install dependencies from apt repos
# * build-essential takes care of what is needed to build the lap binaries
ARG DEBIAN_FRONTEND=noninteractive 
  RUN apt-get update -qq \
  && apt-get install -y supervisor build-essential pkg-config python3 python3-pip \
  && rm -rf /var/lib/apt/lists/*

RUN ln -s /usr/bin/python3 /usr/bin/python

# Configure supervisord
RUN <<EOF cat >> /stop-supervisor.sh
#!/usr/bin/env bash
set -Eeo pipefail
while read -r; do
  echo -e "\e[31m Service was stopped or one of its services crashed,
            see the logs above for more details. \e[0m" >&2
  kill -SIGTERM "$(cat supervisord.pid)"
done < /dev/stdin
EOF
RUN chmod 755 /stop-supervisor.sh

RUN <<EOF cat >> /etc/supervisor/conf.d/supervisord.conf
[supervisord]
nodaemon=true
user=root
logfile=/var/log/supervisor/supervisord.log 
pidfile=/var/run/supervisord.pid
childlogdir=/var/log/supervisor

[program:api-server]
directory=/app/
command=python /app/server.py
stdout_logfile=/dev/stdout
stdout_logfile_maxbytes=0
stderr_logfile=/dev/stdout
stderr_logfile_maxbytes=0

[program:notebook-server]
directory=/app/
command=jupyter notebook --allow-root --no-browser --ServerApp.base_url=/jupyter --ServerApp.allow_origin='*' --port=8888 --ip=0.0.0.0
stdout_logfile=/dev/stdout
stdout_logfile_maxbytes=0
stderr_logfile=/dev/stdout
stderr_logfile_maxbytes=0

[eventlistener:processes]
directory=/app/
command=/stop-supervisor.sh
events=PROCESS_STATE_STOPPED,PROCESS_STATE_EXITED,PROCESS_STATE_FATAL
stderr_logfile=/dev/stdout
stderr_logfile_maxbytes=0
EOF

# Copy application code
COPY . .

# Install application dependencies
RUN pip install pipenv
RUN pipenv lock && pipenv --clear && pipenv --rm
RUN pipenv install --dev --deploy --system

# Install jupyter and notebook-only dependencies
# (not added to Pipfile as it doesn't make sense to include it as part of the 
#  API server -- if it's desired outside of this docker config then venv
#  kernels must be compiled on the host etc.)
# Note: do this after installing application dependencies so that numpy is
#       available as a build dependency for lap
RUN pip install --no-cache-dir --upgrade -r /app/notebooks/notebook_requirements.txt

CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
