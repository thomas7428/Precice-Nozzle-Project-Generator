#!/bin/bash
# Clean CalculiX simulation results for the nozzle solid
cd "$(dirname "$0")"
rm -f *.dat *.frd *.sta *.cvg *.sol *.msg *.prt *.inp~ log.ccx
