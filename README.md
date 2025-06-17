# PreCICE Nozzle Project Generator

This project provides a Python tool to automatically generate a coupled simulation setup for a rocket nozzle using PreCICE, OpenFOAM, and CalculiX. The generator uses user-provided GMSH meshes and optimized templates for each solver.

## Features
- Accepts mesh files for:
  - Solid nozzle with cooling channels (CalculiX)
  - Interior fluid (OpenFOAM)
  - Exterior fluid (OpenFOAM)
  - Cooling channel fluid (OpenFOAM)
- Generates a ready-to-run simulation project with correct configuration for PreCICE coupling.
- Only a portion of the nozzle (fraction of pi) is studied.

## Usage
1. Place your mesh files in the specified input directory.
2. Run the Python script to generate the simulation project.
3. Follow the generated instructions to run the coupled simulation.

## Project Structure
- `templates/` — Contains template configuration files for OpenFOAM, CalculiX, and PreCICE.
- `scripts/` — Contains the main Python generator script.
- `.github/copilot-instructions.md` — Custom Copilot instructions for this workspace.

---

For more details, see the documentation in each template and script file.
