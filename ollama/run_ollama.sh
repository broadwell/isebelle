#!/bin/bash

echo "Starting Ollama server..."
ollama serve &
ollama run since2006/gte-Qwen2-7B-instruct:Q4_K_M

echo "Waiting for Ollama server to be active..."
while [ "$(ollama list | grep 'NAME')" == "" ]; do
  sleep 1
done