#!/bin/bash
# Run CalculiX simulation for the nozzle solid
cd "$(dirname "$0")"
ccx nozzle > log.ccx 2>&1
