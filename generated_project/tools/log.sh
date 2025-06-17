#!/usr/bin/env bash
# Minimal logging utility for preCICE tutorial participants

LOGFILE="log.$(basename $(pwd))"

close_log() {
    echo "Log closed at $(date)" >> "$LOGFILE"
}
