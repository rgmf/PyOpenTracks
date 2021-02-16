#!/bin/bash

if [ -z $1 ]; then
    echo "Usage: $0 lang"
    exit
fi
lang="$1"

if [ -f "${lang}.po" ]; then
    if [ -f "${lang}.mo" ]; then
	rm ${lang}.mo
    fi
    msgfmt -o ${lang}.mo ${lang}
else
    echo "${lang}.po doesn't exists"
fi
