#!/bin/bash
# Startup script for the frontend server

cd "$(dirname "$0")/frontend"
python3 -m http.server 8080

