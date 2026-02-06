#!/usr/bin/env bash
set -e

# Export environment variables with defaults if not set
export OLLAMA_HOST="${OLLAMA_HOST:-0.0.0.0}"
export OLLAMA_NUM_PARALLEL="${OLLAMA_NUM_PARALLEL:-1}"
export OLLAMA_GPU_OVERHEAD="${OLLAMA_GPU_OVERHEAD:-0}"
export ZE_ENABLE_PCI_ID_DEVICE_ORDER="${ZE_ENABLE_PCI_ID_DEVICE_ORDER:-1}"

# Additional Intel GPU environment variables
export ZES_ENABLE_SYSMAN="${ZES_ENABLE_SYSMAN:-1}"

# Execute Ollama with the proper environment
exec /usr/bin/ollama serve "$@"