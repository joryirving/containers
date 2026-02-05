#!/bin/bash
set -e

# Use environment variables with sensible defaults for Intel GPU support
export OLLAMA_HOST="${OLLAMA_HOST:-0.0.0.0}"
export OLLAMA_INTEL_GPU="${OLLAMA_INTEL_GPU:-true}"
export OLLAMA_NUM_GPU="${OLLAMA_NUM_GPU:-999}"
export OLLAMA_CONTEXT_LENGTH="${OLLAMA_CONTEXT_LENGTH:-65536}"
export ZES_ENABLE_SYSMAN="${ZES_ENABLE_SYSMAN:-1}"
export no_proxy="${no_proxy:-localhost,127.0.0.1}"

# Execute Ollama with the proper environment
exec /usr/bin/ollama serve