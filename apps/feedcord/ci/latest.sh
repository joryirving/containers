#!/usr/bin/env bash
version=$(curl -H "Accept: application/vnd.github+json" https://api.github.com/repos/Qolors/FeedCord/releases | jq  -r 'sort_by(.published_at) | reverse | .[].name | select( index("CLI") )' | sed 's:.*CLI v::' | head -n 1)
version="${version#*v}"
printf "%s" "${version}"
