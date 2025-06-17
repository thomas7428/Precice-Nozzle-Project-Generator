#!/bin/bash
# Clean OpenFOAM simulation results for cooling channel region
cd "$(dirname "$0")"
rm -rf processor* constant/polyMesh log.* [1-9]*
