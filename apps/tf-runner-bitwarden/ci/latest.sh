#!/usr/bin/env bash
version="$(curl -sX GET "https://api.github.com/repos/weaveworks/tf-controller/tags" | jq --raw-output '.[0].name' 2>/dev/null)"
version="${version#*v}"
printf "%s" "${version}"
