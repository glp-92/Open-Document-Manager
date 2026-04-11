leann build test --docs /documents/ \
  --embedding-mode ollama --embedding-model nomic-cpu \
  --backend hnsw \
  --force
leann ask test --interactive --model qwen3:1.7b
leann ask test --interactive \
  --model llm-gpu:latest \
  --top-k 3