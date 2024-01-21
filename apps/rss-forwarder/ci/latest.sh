#!/usr/bin/env bash
version="$(curl -sX GET "https://api.github.com/repos/morphy2k/rss-forwarder/releases/latest" | jq --raw-output '.tag_name' 2>/dev/null)"
version="${version#*v}"
version="${version#*release-}"
version="0.7.0-beta.2" #hardcode this for now
printf "%s" "${version}"
