#!/usr/bin/env bash
version="$(curl -sX GET "https://api.github.com/repos/j6nca/free-game-notifier/releases/latest" | jq --raw-output '.tag_name' 2>/dev/null)"
version="${version#*v}"
version="${version#*release-}"
verision="latest" # hardcoded until semantic versioning is implemented
printf "%s" "${version}"
