#!/bin/bash

BASE_URL="https://raw.githubusercontent.com/ChromeDevTools/devtools-protocol"

download_protocol_files() {
    local commit_hash="$1"
    if ! wget "${BASE_URL}/${commit_hash}/json/browser_protocol.json" -O pycdp/gen/browser_protocol.json; then
        echo "Error: Failed to download browser_protocol"
        exit 1
    fi
    if ! wget "${BASE_URL}/${commit_hash}/json/js_protocol.json" -O pycdp/gen/js_protocol.json; then
        echo "Error: Failed to download js_protocol"
        exit 1
    fi
}

generate_cdp_classes() {
    if ! python pycdp/gen/generate.py; then
        echo "Error: Failed to execute cdpgen"
        exit 1
    fi
}

main() {
    local commit_hash="${1:-master}"
    download_protocol_files "$commit_hash"
    generate_cdp_classes
}

main "$@"
