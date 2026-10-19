#!/usr/bin/env bash
set -euo pipefail
umask 077

: "${PASEO_PASSWORD:?PASEO_PASSWORD must be set and non-empty}"
: "${LITELLM_API_KEY:?LITELLM_API_KEY must be set and non-empty}"

OPENCODE_CONFIG_DIR="${HOME}/.config/opencode"

mkdir -p "${PASEO_HOME}" "${OPENCODE_CONFIG_DIR}" "${HOME}/.agents/skills" \
  "${MISE_DATA_DIR}/shims" "${MISE_CACHE_DIR}" "${MISE_STATE_DIR}" \
  "${HOME}/.config/mise"
install -m 600 /etc/paseo/paseo.json "${PASEO_HOME}/config.json"
install -m 600 /etc/paseo/opencode.json "${OPENCODE_CONFIG_DIR}/opencode.json"

# Keep packaged supervisor and entrypoint behavior, running uid 1000.
exec /usr/local/bin/paseo-docker-entrypoint
