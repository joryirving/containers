#!/bin/bash
set -e

# Use environment variables with sensible defaults for Intel GPU support
export OLLAMA_HOST="${OLLAMA_HOST:-0.0.0.0}"
export OLLAMA_NUM_PARALLEL="${OLLAMA_NUM_PARALLEL:-1}"
export OLLAMA_GPU_OVERHEAD="${OLLAMA_GPU_OVERHEAD:-0}"
export ZE_ENABLE_PCI_ID_DEVICE_ORDER="${ZE_ENABLE_PCI_ID_DEVICE_ORDER:-1}"

# Execute Ollama with the proper environment
exec /usr/bin/ollama serve