#!/usr/bin/env bash
set -e -u

. ../tools/log.sh
exec > >(tee --append "$LOGFILE") 2>&1

if [ ! -f mesh.inp ]; then
    echo "Mesh file mesh.inp not found. Please ensure the mesh is present."
    exit 1
fi

export CCX_NPROC_EQUATION_SOLVER=1
ccx_preCICE -i solid -precice-participant Solid

close_log
