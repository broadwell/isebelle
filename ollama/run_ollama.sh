#!/bin/bash

echo "Starting Ollama server..."
export OLLAMA_HOST="http://ollama:11434"
ollama serve &
echo "Waiting for Ollama server to be active..."
while [ "$(ollama list | grep 'NAME')" == "" ]; do
  sleep 1
done
ollama run since2006/gte-Qwen2-7B-instruct:Q4_K_M