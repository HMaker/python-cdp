#!/bin/bash

clean_devtools_directory() {
    if [ -d "devtools-protocol" ] && { [ -f "devtools-protocol/browser_protocol.json" ] || [ -f "devtools-protocol/js_protocol.json" ]; }; then
        rm -f devtools-protocol/*
    fi
}

download_protocol_files() {
    if ! wget -P devtools-protocol/ https://raw.githubusercontent.com/ChromeDevTools/devtools-protocol/master/json/browser_protocol.json https://raw.githubusercontent.com/ChromeDevTools/devtools-protocol/master/json/js_protocol.json; then
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
    clean_devtools_directory
    download_protocol_files
    generate_cdp_classes
    delete_devtools_directory
}

main
