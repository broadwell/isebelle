FROM debian:stable-slim
#FROM ollama

WORKDIR /tmp
EXPOSE 11434

RUN apt-get update -qq \
  && apt-get install -y curl \
  && rm -rf /var/lib/apt/lists/*

RUN curl -fsSL https://ollama.com/install.sh | sh

COPY ./run_ollama.sh /tmp/run_ollama.sh

RUN chmod +x run_ollama.sh

CMD ["/usr/bin/sh", "/tmp/run_ollama.sh"]