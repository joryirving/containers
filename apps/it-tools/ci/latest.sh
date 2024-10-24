#!/usr/bin/env bash
version="$(curl -sX GET "https://api.github.com/repos/CorentinTh/it-tools/releases/latest" | jq --raw-output '.tag_name' || true)"
version="${version#*v}"
version="${version#*release-}"
printf "%s" "${version}"
