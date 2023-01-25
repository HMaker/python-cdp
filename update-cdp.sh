#!/bin/bash

if [ -d "devtools-protocol" ] && { [ -f "devtools-protocol/browser_protocol.json" ] || [ -f "devtools-protocol/js_protocol.json" ]; }; then
    rm -f devtools-protocol/*
fi

wget -P devtools-protocol/ https://raw.githubusercontent.com/ChromeDevTools/devtools-protocol/master/json/browser_protocol.json https://raw.githubusercontent.com/ChromeDevTools/devtools-protocol/master/json/js_protocol.json
if [ $? -ne 0 ]; then
    echo "Error: Failed to download files"
    exit 1
fi

cdpgen --browser-protocol devtools-protocol/browser_protocol.json --js-protocol devtools-protocol/js_protocol.json --output cdp/
if [ $? -ne 0 ]; then
    echo "Error: Failed to execute cdpgen"
    exit 1
fi