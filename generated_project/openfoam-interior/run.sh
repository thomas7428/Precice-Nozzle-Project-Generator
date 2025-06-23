#!/usr/bin/env bash
set -e -u

. ../../tools/log.sh
exec > >(tee --append "$LOGFILE") 2>&1

if [ ! -f mesh.msh ]; then
    echo "Mesh file mesh.msh not found. Please ensure the mesh is present."
    exit 1
fi

blockMesh
# Add mesh conversion if needed

decomposePar
mpirun -np 4 preciceAdapterFunctionObject -case . -participant FluidInner
reconstructPar

close_log
