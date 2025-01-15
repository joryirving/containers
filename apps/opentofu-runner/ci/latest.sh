#!/usr/bin/env bash
version=$(curl -sX GET "https://api.github.com/repos/opentofu/opentofu/releases/latest" | jq --raw-output '.tag_name')
version="${version#*v}"
version="${version#*release-}"
printf "%s" "${version}"
