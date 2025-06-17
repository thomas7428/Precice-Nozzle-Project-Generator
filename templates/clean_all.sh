#!/bin/bash
# Unified clean script for all participants
set -e
cd $(dirname "$0")

cd calculix && ./clean.sh && cd ..
for region in openfoam/interior openfoam/exterior openfoam/cooling_channel; do
    cd $region && ./clean.sh && cd - > /dev/null
done

rm -rf precice/log.*
rm -rf results/
echo "All participants cleaned."
