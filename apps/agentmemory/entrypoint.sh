#!/bin/sh
# agentmemory entrypoint.
#
# Three modes:
#
# 1. Pre-provided secret (preferred): AGENTMEMORY_SECRET is set in the
#    environment (typically from a K8s Secret backed by 1Password / Vault).
#    Use it as-is, skip the HMAC file entirely.
#
# 2. Auto-generated secret (fallback for first boot when env is unset):
#    generate 256-bit HMAC with openssl rand, write to
#    ${AGENTMEMORY_HMAC_FILE} (default /data/.hmac, chmod 600), print
#    to stdout once so the operator can capture it from pod logs
#    (kubectl logs deploy/agentmemory -n ai). On subsequent boots load
#    the existing file. Rotate by deleting the file and restarting.
#
# 3. MCP shim mode (first arg is "mcp"): skip the entire secret dance.
#    AGENTMEMORY_SECRET must come via env from the deployed server's
#    secret; the shim proxies to the server via AGENTMEMORY_URL.

set -eu

if [ "${1:-}" != "mcp" ] && [ -z "${AGENTMEMORY_SECRET:-}" ]; then
    HMAC_FILE="${AGENTMEMORY_HMAC_FILE:-/data/.hmac}"
    DATA_DIR="${AGENTMEMORY_DATA_DIR:-/data}"

    mkdir -p "${DATA_DIR}"

    if [ ! -s "${HMAC_FILE}" ]; then
      SECRET="$(openssl rand -hex 32)"
      umask 077
      printf '%s\n' "${SECRET}" > "${HMAC_FILE}"
      chmod 600 "${HMAC_FILE}"
      echo "================================================================"
      echo "agentmemory: generated HMAC secret on first boot"
      echo "AGENTMEMORY_SECRET=${SECRET}"
      echo "Copy this value now. It will not be printed again."
      echo "Stored at: ${HMAC_FILE} (chmod 600)"
      echo "To rotate: delete ${HMAC_FILE} on the persistent volume and restart."
      echo "================================================================"
    fi

    AGENTMEMORY_SECRET="$(cat "${HMAC_FILE}")"
    export AGENTMEMORY_SECRET
fi

exec agentmemory "$@"