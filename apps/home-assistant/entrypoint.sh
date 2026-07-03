#!/usr/bin/env bash

unset UV_SYSTEM_PYTHON

mkdir -p "${VENV_FOLDER}"
uv venv --system-site-packages --link-mode=copy --allow-existing "${VENV_FOLDER}"
source "${VENV_FOLDER}/bin/activate"

# System site-packages (baked into the image) acts as a find-links index.
site_packages=$(python -c "import sysconfig; print(sysconfig.get_path('purelib'))")

# Reconcile the persisted venv with the image's pinned deps on every boot.
# Without this, a stale aiohttp (or any other dep) carried over in the PVC
# shadows the image's newer version and breaks HA at runtime (e.g. HA's
# websocket_api passing `decode_text=` to an aiohttp that predates it).
uv pip install \
    --no-index \
    --find-links="${site_packages}" \
    uv \
    "homeassistant==${VERSION}"

ln -sf /proc/self/fd/1 /config/home-assistant.log

exec \
    python3 -m homeassistant \
        --config /config \
        "$@"
