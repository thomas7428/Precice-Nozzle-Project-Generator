import os
import shutil
from pathlib import Path

"""
precice_nozzle_generator.py

This script generates a PreCICE-coupled simulation project for a rocket nozzle using user-provided GMSH meshes.
It copies and customizes template files for OpenFOAM, CalculiX, and PreCICE, and places the user meshes in the correct locations.
"""

def generate_project(mesh_files, output_dir, fraction_of_pi=1.0):
    """
    mesh_files: dict with keys 'solid', 'interior_fluid', 'exterior_fluid', 'cooling_channel_fluid'
    output_dir: path to the generated project
    fraction_of_pi: float, portion of the nozzle to study (e.g., 0.5 for half-pi)
    """
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)

    # Copy template files
    template_dir = Path(__file__).parent.parent / 'templates'
    for item in template_dir.iterdir():
        if item.is_dir():
            shutil.copytree(item, Path(output_dir) / item.name, dirs_exist_ok=True)
        else:
            shutil.copy2(item, output_dir)

    # Place mesh files
    mesh_map = {
        'solid': 'calculix/mesh.msh',
        'interior_fluid': 'openfoam/interior/mesh.msh',
        'exterior_fluid': 'openfoam/exterior/mesh.msh',
        'cooling_channel_fluid': 'openfoam/cooling_channel/mesh.msh',
    }
    for key, dest in mesh_map.items():
        if key in mesh_files:
            dest_path = Path(output_dir) / dest
            os.makedirs(dest_path.parent, exist_ok=True)
            shutil.copy2(mesh_files[key], dest_path)

    # Adjust configuration files (PreCICE, OpenFOAM, CalculiX)
    # TODO: Implement template variable replacement for fraction_of_pi and mesh names
    print(f"Project generated at {output_dir}. Please review configuration files.")

if __name__ == "__main__":
    # Example usage
    mesh_files = {
        'solid': 'path/to/solid.msh',
        'interior_fluid': 'path/to/interior.msh',
        'exterior_fluid': 'path/to/exterior.msh',
        'cooling_channel_fluid': 'path/to/cooling_channel.msh',
    }
    generate_project(mesh_files, 'generated_project', fraction_of_pi=0.5)
