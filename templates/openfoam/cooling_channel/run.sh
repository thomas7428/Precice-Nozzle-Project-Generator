#!/bin/bash
# Run OpenFOAM simulation for cooling channel region
cd "$(dirname "$0")"
blockMesh > log.blockMesh 2>&1
# Replace with actual mesh conversion if needed
decomposePar > log.decomposePar 2>&1
mpirun -np 4 icoFoam -parallel > log.foam 2>&1
reconstructPar > log.reconstructPar 2>&1
