# PreCICE Nozzle Project (Generated)

This project is a fully automated setup for a PreCICE-coupled simulation of a rocket nozzle using OpenFOAM (fluid) and CalculiX (solid), based on user-provided GMSH meshes.

## Project Structure
- `calculix/` — Solid domain (CalculiX input, mesh, scripts)
- `openfoam/`
  - `interior/` — Interior fluid region (OpenFOAM)
  - `exterior/` — Exterior fluid region (OpenFOAM)
  - `cooling_channel/` — Cooling channel fluid (OpenFOAM)
- `precice/` — PreCICE coupling configuration
- `meshs/` — All mesh files used in the simulation
- `run_all.sh` — Run all participants and PreCICE coupling
- `clean_all.sh` — Clean all simulation results

## How to Run
1. Ensure all required mesh files are present in `meshs/`:
   - `Solid_mesh.msh` (solid)
   - `Inner_Fluid_mesh.msh` (interior fluid)
   - `Outer_Fluid_mesh.msh` (exterior fluid)
   - `Cooling_Channels_mesh.msh` (cooling channel fluid)
2. Review and edit `config.yaml` for simulation/material/environment/coupling parameters.
3. Run the unified script:
   ```bash
   ./run_all.sh
   ```
   This will launch all OpenFOAM, CalculiX, and PreCICE participants.

## Cleaning Up
To remove all simulation results and logs:
```bash
./clean_all.sh
```

## Validation
After generation, the project is automatically validated for:
- Missing required files
- Unreplaced placeholders
- Mesh/interface consistency

If any issues are detected, they will be printed in the terminal. Please fix them before running the simulation.

## Troubleshooting
- Ensure all mesh files are GMSH 4.x format and contain correct physical names for interfaces.
- Check that all config placeholders are replaced in the generated files.
- For advanced configuration, edit the files in `openfoam/`, `calculix/`, and `precice/` as needed.

## More Information
- See the main project documentation or PreCICE tutorials for details on coupled FSI simulations.
