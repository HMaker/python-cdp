#!/bin/bash

BASE_URL="https://raw.githubusercontent.com/ChromeDevTools/devtools-protocol"

clean_devtools_directory() {
    if [ -d "devtools-protocol" ] && { [ -f "devtools-protocol/browser_protocol.json" ] || [ -f "devtools-protocol/js_protocol.json" ]; }; then
        rm -f devtools-protocol/*
    fi
}

download_protocol_files() {
    local commit_hash="$1"
    if ! wget -P devtools-protocol/ "${BASE_URL}/${commit_hash}/json/browser_protocol.json" "${BASE_URL}/${commit_hash}/json/js_protocol.json"; then
        echo "Error: Failed to download files"
        exit 1
    fi
}

generate_cdp_classes() {
    if ! cdpgen --browser-protocol devtools-protocol/browser_protocol.json --js-protocol devtools-protocol/js_protocol.json --output pycdp/cdp/; then
        echo "Error: Failed to execute cdpgen"
        exit 1
    fi
}

delete_devtools_directory() {
    if [ -d "devtools-protocol" ]; then
        rm -r devtools-protocol
        echo "Deleted devtools-protocol folder"
    fi
}

main() {
    local commit_hash="${1:-master}"
    clean_devtools_directory
    download_protocol_files "$commit_hash"
    generate_cdp_classes
    delete_devtools_directory
}

main "$@"
