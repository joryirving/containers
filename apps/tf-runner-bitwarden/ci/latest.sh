#!/usr/bin/env bash
version="$(curl -sX GET "https://api.github.com/repos/weaveworks/tf-controller/tags" | jq --raw-output '.[0].name' 2>/dev/null)"
version="${version#*v}"
printf "%s" "${version}"

bw_version=$(curl -H "Accept: application/vnd.github+json" https://api.github.com/repos/bitwarden/clients/releases | jq  -r 'sort_by(.published_at) | reverse | .[].name | select( index("CLI") )' | sed 's:.*CLI v::' | head -n 1)
bw_version="${bw_version#*v}"
bw_version="${bw_version#*cli-}"
printf "%s" "${bw_version}"
