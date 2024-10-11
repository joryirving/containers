#!/usr/bin/env bash
version="$(curl -sX GET "https://api.github.com/repos/CorentinTh/it-tools/releases/latest" | jq --raw-output '.tag_name' || true)"
version="${version#*v}"
version="${version#*release-}"
fullversion="${version#*release-}"
version="${version%%-*}"
printf "%s" "${version}"
printf "%s" "${fullversion}"
