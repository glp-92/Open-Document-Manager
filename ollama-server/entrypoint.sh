#!/bin/bash
/bin/ollama serve &
pid=$!
sleep 5
echo "Waiting for Ollama to start..."
until ollama list > /dev/null 2>&1; do
  sleep 2
done
# MODEL=$(echo "${MODEL_NAME:-qwen3.5:2b}" | tr -d '"' | tr -d "'")
# echo "Downloading model ${MODEL}..."
# ollama pull "${MODEL}"
ollama create "${EMBEDDING_MODEL}" -f /models/Modelfile-embeddings-cpu
ollama create "${LLM_MODEL}" -f /models/Modelfile-llm-gpu
echo "Done!"
wait $pid