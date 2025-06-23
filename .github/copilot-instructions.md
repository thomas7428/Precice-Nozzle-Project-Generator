<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->

This project is a Python tool to generate a PreCICE simulation setup for a rocket nozzle using OpenFOAM and CalculiX, based on user-provided GMSH meshes. The generator should:
- Accept mesh files for: solid (CalculiX), interior fluid (OpenFOAM), exterior fluid (OpenFOAM), and cooling channel fluid (OpenFOAM).
- Use templates for OpenFOAM, CalculiX, and PreCICE configuration, optimized for this application.
- Automate mesh placement and configuration adjustment for a coupled simulation.
- Only a portion of the nozzle (fraction of pi) is studied.
