#!/bin/sh

if [[ -n $(find . -name "*.so") ]] ; then
    echo "Found .so file(s):"
    find . -name "*.so"
    exit 1
fi
