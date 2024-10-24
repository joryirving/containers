#!/usr/bin/env bash
version="$(curl -sX GET "https://api.github.com/repos/caddyserver/caddy/releases/latest" | jq --raw-output '.tag_name' || true)"
version="${version#*v}"
version="${version#*release-}"
printf "%s" "${version}"
