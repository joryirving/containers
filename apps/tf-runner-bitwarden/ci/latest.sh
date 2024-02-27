#!/usr/bin/env bash
version="$(curl -sX GET "https://api.github.com/repos/flux-iac/tofu-controller/tags" | jq --raw-output '.[].name' 2>/dev/null | grep -E '^v[0-9]+\.[0-9]+\.[0-9]+$' | sort -V | tail -n 1)"
version="${version#*v}"
printf "%s" "${version}"
