#!/bin/bash
# Unified run script for all participants
set -e
cd $(dirname "$0")

# Run CalculiX
cd calculix && ./run.sh &
CCX_PID=$!
cd ..

# Run OpenFOAM participants
for region in openfoam/interior openfoam/exterior openfoam/cooling_channel; do
    cd $region && ./run.sh &
    cd - > /dev/null
    sleep 1
done

wait $CCX_PID
wait

echo "All participants finished."
