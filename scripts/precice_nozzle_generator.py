import os
import shutil
from pathlib import Path
import re
import yaml
import glob
import sys

"""
precice_nozzle_generator.py

This script generates a PreCICE-coupled simulation project for a rocket nozzle using user-provided GMSH meshes.
It copies and customizes template files for OpenFOAM, CalculiX, and PreCICE, and places the user meshes in the correct locations.
It also parses mesh boundaries to adapt configuration files.
"""

def parse_physical_names(mesh_path):
    """Parse the $PhysicalNames section of a GMSH .msh file and return a dict of {id: name}."""
    names = {}
    with open(mesh_path, 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()
    try:
        start = lines.index('$PhysicalNames\n')
        count = int(lines[start+1])
        for i in range(count):
            parts = lines[start+2+i].strip().split(' ', 2)
            if len(parts) == 3:
                _, phys_id, name = parts
                names[int(phys_id)] = name.strip('"')
    except Exception as e:
        print(f"Could not parse $PhysicalNames in {mesh_path}: {e}")
    return names

def find_interfaces(physical_names, pattern):
    """Return a list of physical names matching a regex pattern."""
    return [name for name in physical_names.values() if re.search(pattern, name)]

def replace_in_file(filepath, replacements):
    """Replace placeholders in a file with values from the replacements dict."""
    with open(filepath, 'r') as f:
        content = f.read()
    for key, value in replacements.items():
        content = content.replace(key, value)
    with open(filepath, 'w') as f:
        f.write(content)

def replace_in_dir(directory, replacements):
    for filepath in glob.glob(f"{directory}/**", recursive=True):
        if os.path.isfile(filepath):
            replace_in_file(filepath, replacements)

def parse_gmsh_mesh(mesh_path):
    """Parse a GMSH .msh file and return nodes, elements, and physical sets."""
    nodes = {}
    elements = []
    phys_sets = {}
    with open(mesh_path, 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()
    # Find $Nodes and $Elements sections
    try:
        node_start = lines.index('$Nodes\n') + 1
        num_nodes = int(lines[node_start])
        node_lines = lines[node_start+1:node_start+1+num_nodes]
        for line in node_lines:
            parts = line.strip().split()
            if len(parts) >= 4:
                node_id = int(parts[0])
                coords = tuple(map(float, parts[1:4]))
                nodes[node_id] = coords
        elem_start = lines.index('$Elements\n') + 1
        num_elems = int(lines[elem_start])
        elem_lines = lines[elem_start+1:elem_start+1+num_elems]
        for line in elem_lines:
            parts = line.strip().split()
            if len(parts) >= 4:
                elem_id = int(parts[0])
                elem_type = int(parts[1])
                phys_grp = int(parts[3])
                conn = list(map(int, parts[4:]))
                elements.append((elem_id, elem_type, phys_grp, conn))
                if phys_grp not in phys_sets:
                    phys_sets[phys_grp] = []
                phys_sets[phys_grp].append(elem_id)
    except Exception as e:
        print(f"Error parsing mesh: {e}")
    return nodes, elements, phys_sets

def parse_gmsh_mesh_v4(mesh_path):
    """Parse a GMSH 4.x .msh file and return nodes, elements, and physical sets."""
    nodes = {}
    elements = []
    phys_sets = {}
    with open(mesh_path, 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()
    # Parse $Nodes
    try:
        node_start = lines.index('$Nodes\n') + 1
        header = list(map(int, lines[node_start].split()))
        num_entity_blocks = header[0]
        node_lines = []
        idx = node_start + 1
        for _ in range(num_entity_blocks):
            ent_hdr = list(map(int, lines[idx].split()))
            num_nodes_in_block = ent_hdr[3]
            idx += 1  # skip header
            idx += 1  # skip parametric flag line
            for _ in range(num_nodes_in_block):
                node_id = int(lines[idx].strip())
                idx += 1
                coords = tuple(map(float, lines[idx].strip().split()))
                nodes[node_id] = coords
                idx += 1
        # Parse $Elements
        elem_start = lines.index('$Elements\n') + 1
        elem_header = list(map(int, lines[elem_start].split()))
        num_elem_blocks = elem_header[0]
        idx = elem_start + 1
        for _ in range(num_elem_blocks):
            ent_hdr = list(map(int, lines[idx].split()))
            entity_dim, entity_tag, elem_type, num_elems_in_block = ent_hdr
            idx += 1
            for _ in range(num_elems_in_block):
                parts = lines[idx].strip().split()
                elem_id = int(parts[0])
                conn = list(map(int, parts[1:]))
                elements.append((elem_id, elem_type, entity_tag, conn))
                if entity_tag not in phys_sets:
                    phys_sets[entity_tag] = []
                phys_sets[entity_tag].append(elem_id)
                idx += 1
    except Exception as e:
        print(f"Error parsing mesh: {e}")
    return nodes, elements, phys_sets

def write_calculix_inp(nodes, elements, phys_names, phys_sets, out_path):
    with open(out_path, 'w') as f:
        f.write('*Heading\n** Auto-generated CalculiX input\n')
        f.write('*Node\n')
        for node_id, coords in nodes.items():
            f.write(f"{node_id}, {coords[0]}, {coords[1]}, {coords[2]}\n")
        f.write('*Element, type=C3D4\n')
        for elem_id, elem_type, phys_grp, conn in elements:
            if elem_type == 4:  # Tetrahedral
                f.write(f"{elem_id}, {', '.join(map(str, conn))}\n")
        # Write element sets for each physical group
        for phys_id, name in phys_names.items():
            if phys_id in phys_sets:
                f.write(f"*Elset, elset={name}\n")
                f.write(','.join(map(str, phys_sets[phys_id])) + '\n')
        # ...existing material, boundary, and coupling...
        f.write('*MATERIAL, NAME=STEEL\n*ELASTIC\n210000, 0.3\n*DENSITY\n7850\n*CONDUCTIVITY\n45\n*SPECIFIC HEAT\n500\n')
        f.write('*STEP\n*STATIC\n*END STEP\n')

def load_config(config_path):
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def flatten_config(config, prefix=''):  # Helper to flatten nested config for template replacement
    items = {}
    if isinstance(config, dict):
        for k, v in config.items():
            key = f"{prefix}{k}" if prefix else k
            items.update(flatten_config(v, prefix=key+'.'))
    elif isinstance(config, list):
        for idx, v in enumerate(config):
            key = f"{prefix}{idx}"
            items.update(flatten_config(v, prefix=key+'.'))
    else:
        items[prefix[:-1]] = str(config)
    return items

def update_precice_xml(xml_path, mesh_files, interfaces):
    with open(xml_path, 'r') as f:
        content = f.read()
    # Replace mesh file placeholders
    content = content.replace('INTERIOR_MESH', mesh_files['interior_fluid'])
    content = content.replace('EXTERIOR_MESH', mesh_files['exterior_fluid'])
    content = content.replace('COOLING_MESH', mesh_files['cooling_channel_fluid'])
    content = content.replace('SOLID_MESH', mesh_files['solid'])
    # Optionally, replace interface names if needed
    # Example: content = content.replace('NOZZLE_WALL', interfaces['nozzle_wall'])
    with open(xml_path, 'w') as f:
        f.write(content)

def generate_openfoam_boundary_field(patch_names, patch_type='preciceAdapter'):
    bf = 'boundaryField\n{\n'
    for patch in patch_names:
        bf += f'    {patch}\n    {{\n        type            {patch_type};\n    }}\n'
    bf += '}\n'
    return bf

def write_openfoam_boundaries(output_dir, region, patch_names):
    # Update 0/U and 0/p with all FSI patches
    for field in ['U', 'p']:
        file_path = os.path.join(output_dir, f'openfoam/{region}/0/{field}')
        with open(file_path, 'w') as f:
            f.write(generate_openfoam_boundary_field(patch_names))

def write_calculix_surfaces(f, fsi_sets):
    # Write *Elset and *Surface for each FSI interface
    for name, elems in fsi_sets.items():
        f.write(f"*Elset, elset={name}\n")
        f.write(','.join(map(str, elems)) + '\n')
        f.write(f"*Surface, name={name}, type=ELEMENT\n{name}, S1\n")

def update_precice_xml_interfaces(xml_path, interface_names):
    with open(xml_path, 'r') as f:
        content = f.read()
    for name in interface_names:
        content = content.replace(f'INTERFACE_{name}', name)
    with open(xml_path, 'w') as f:
        f.write(content)

def generate_project(mesh_files, output_dir, fraction_of_pi=1.0, config_path='config.yaml', combustion=False):
    config = load_config(config_path)
    config_flat = flatten_config(config)

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

    # Copy tools/log.sh to project root for logging in all run.sh scripts
    tools_dir = template_dir / 'tools'
    if tools_dir.exists():
        for item in tools_dir.iterdir():
            shutil.copy2(item, Path(output_dir) / 'tools' / item.name)
    else:
        os.makedirs(Path(output_dir) / 'tools', exist_ok=True)
        # fallback: create a minimal log.sh if missing
        with open(Path(output_dir) / 'tools/log.sh', 'w') as f:
            f.write('#!/usr/bin/env bash\nLOGFILE="log.$(basename $(pwd))"\nclose_log() { echo "Log closed at $(date)" >> "$LOGFILE"; }\n')

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

    # Copy mesh files into generated_project/meshs
    mesh_dir = Path(output_dir) / 'meshs'
    os.makedirs(mesh_dir, exist_ok=True)
    for key, src in mesh_files.items():
        dest = mesh_dir / Path(src).name
        shutil.copy2(src, dest)
        mesh_files[key] = str(dest)

    # CalculiX mesh automation (GMSH 4.x)
    nodes, elements, phys_sets = parse_gmsh_mesh_v4(mesh_files['solid'])
    solid_names = parse_physical_names(mesh_files['solid'])
    write_calculix_inp(nodes, elements, solid_names, phys_sets, Path(output_dir) / 'calculix/nozzle.inp')

    # Parse mesh boundaries
    solid_names = parse_physical_names(mesh_files['solid'])
    inner_names = parse_physical_names(mesh_files['interior_fluid'])
    outer_names = parse_physical_names(mesh_files['exterior_fluid'])
    cooling_names = parse_physical_names(mesh_files['cooling_channel_fluid'])

    # Example: find all nozzle wall interfaces for FSI
    solid_nozzle_walls = find_interfaces(solid_names, r'Nozzle_Outer_Wall')
    outer_nozzle_walls = find_interfaces(outer_names, r'Nozzle_Outer_Wall')
    cooling_entries = find_interfaces(cooling_names, r'Cooling_Channel_\d+_Entry_Wall')
    cooling_exits = find_interfaces(cooling_names, r'Cooling_Channel_\d+_Exit_Wall')

    print("Detected solid nozzle wall surfaces:", solid_nozzle_walls)
    print("Detected outer fluid nozzle wall surfaces:", outer_nozzle_walls)
    print("Detected cooling channel entries:", cooling_entries)
    print("Detected cooling channel exits:", cooling_exits)

    # Prepare replacements for placeholders
    replacements = {
        '{{MESH_PATH}}': mesh_files['solid'],
        '{{INTERIOR_MESH}}': mesh_files['interior_fluid'],
        '{{EXTERIOR_MESH}}': mesh_files['exterior_fluid'],
        '{{COOLING_MESH}}': mesh_files['cooling_channel_fluid'],
        '{{SOLID_MESH}}': mesh_files['solid'],
        '{{FRACTION_OF_PI}}': str(fraction_of_pi),
    }
    # Ensure cooling_solver is set in replacements before any replacements are made
    cooling_solver = config.get('simulation', {}).get('cooling_solver')
    if not cooling_solver:
        if combustion:
            cooling_solver = config.get('simulation', {}).get('reacting_solver', 'reactingFoam')
        else:
            cooling_solver = config.get('simulation', {}).get('solver', 'rhoCentralFoam')
    replacements['{{simulation.cooling_solver}}'] = cooling_solver
    # Example: use first detected wall for coupling
    if solid_nozzle_walls:
        replacements['NOZZLE_WALL'] = solid_nozzle_walls[0]
    if cooling_entries:
        replacements['COOLING_WALL'] = cooling_entries[0]

    # Detect interface names for PreCICE XML
    # These should be the patch/physical names at the fluid-solid interface for each region
    # For this example, use the first matching interface for each region
    # (You may want to improve this logic for multi-channel or multi-patch cases)
    interface_names = {
        'INTERIOR_INTERFACE': find_interfaces(inner_names, r'Inner_Fluid_Outer_Wall')[0] if find_interfaces(inner_names, r'Inner_Fluid_Outer_Wall') else 'MISSING_INTERIOR_INTERFACE',
        'EXTERIOR_INTERFACE': find_interfaces(outer_names, r'Nozzle_Outer_Wall')[0] if find_interfaces(outer_names, r'Nozzle_Outer_Wall') else 'MISSING_EXTERIOR_INTERFACE',
        'COOLING_INTERFACE': find_interfaces(cooling_names, r'Cooling_Channel_\d+_Entry_Wall')[0] if find_interfaces(cooling_names, r'Cooling_Channel_\d+_Entry_Wall') else 'MISSING_COOLING_INTERFACE',
        'SOLID_INTERFACE': find_interfaces(solid_names, r'Nozzle_Outer_Wall')[0] if find_interfaces(solid_names, r'Nozzle_Outer_Wall') else 'MISSING_SOLID_INTERFACE',
    }
    # Add these to replacements for PreCICE XML
    for k, v in interface_names.items():
        replacements[f'{{{{{k}}}}}'] = v

    # Merge config values into replacements
    replacements.update({f'{{{{{k}}}}}': v for k, v in config_flat.items()})
    # Replace in all OpenFOAM files recursively
    for region in ['interior', 'exterior', 'cooling_channel']:
        replace_in_dir(os.path.join(output_dir, f'openfoam/{region}'), replacements)
    # Replace in CalculiX, OpenFOAM, and PreCICE config files
    replace_in_file(Path(output_dir) / 'calculix/nozzle.inp', replacements)
    replace_in_file(Path(output_dir) / 'openfoam/interior/README.txt', replacements)
    replace_in_file(Path(output_dir) / 'openfoam/exterior/README.txt', replacements)
    replace_in_file(Path(output_dir) / 'openfoam/cooling_channel/README.txt', replacements)
    replace_in_file(Path(output_dir) / 'precice/precice-config.xml', replacements)

    # --- Combustion logic ---
    # If combustion is enabled, set solver and copy chemistry/species files for reactingFoam
    if combustion:
        print("[INFO] Generating a combustion (reacting flow) project...")
        # Overwrite solver in replacements
        replacements['{{simulation.solver}}'] = config.get('simulation', {}).get('reacting_solver', 'reactingFoam')
        # Copy all combustion-specific files from templates/openfoam/interior/combustion
        combustion_template_dir = template_dir / 'openfoam/interior/combustion'
        combustion_target_dir = Path(output_dir) / 'openfoam/interior'
        if combustion_template_dir.exists():
            for item in combustion_template_dir.iterdir():
                shutil.copy2(item, combustion_target_dir / item.name)
        # Replace placeholders in all new combustion files
        for item in combustion_template_dir.iterdir():
            target_file = combustion_target_dir / item.name
            if target_file.is_file():
                replace_in_file(target_file, replacements)
    else:
        print("[INFO] Generating a non-combustion (standard CHT) project...")
        replacements['{{simulation.solver}}'] = config.get('simulation', {}).get('solver', 'rhoCentralFoam')

    # Example: collect FSI interface names
    fsi_patches = list(set(solid_nozzle_walls + outer_nozzle_walls + cooling_entries))
    # Write OpenFOAM boundary files for all regions
    for region in ['interior', 'exterior', 'cooling_channel']:
        write_openfoam_boundaries(output_dir, region, fsi_patches)
    # Write CalculiX surfaces for FSI
    # (Assume fsi_sets is a dict {name: [elem_ids]})
    # with open(Path(output_dir) / 'calculix/nozzle.inp', 'a') as f:
    #     write_calculix_surfaces(f, fsi_sets)
    # Update PreCICE XML with interface names
    update_precice_xml_interfaces(os.path.join(output_dir, 'precice/precice-config.xml'), fsi_patches)

    print(f"Project generated at {output_dir}. All files and meshes are included and ready to use.")
    # Validation step
    validate_generated_project(output_dir, mesh_files)

def cli_wizard():
    print("\n==== PreCICE Nozzle Project Generator ====")
    print("You can use default mesh file names or specify your own.")
    mesh_files = {}
    mesh_files['solid'] = input("Path to solid mesh [meshs/Solid_mesh.msh]: ") or 'meshs/Solid_mesh.msh'
    mesh_files['interior_fluid'] = input("Path to interior fluid mesh [meshs/Inner_Fluid_mesh.msh]: ") or 'meshs/Inner_Fluid_mesh.msh'
    mesh_files['exterior_fluid'] = input("Path to exterior fluid mesh [meshs/Outer_Fluid_mesh.msh]: ") or 'meshs/Outer_Fluid_mesh.msh'
    mesh_files['cooling_channel_fluid'] = input("Path to cooling channel mesh [meshs/Cooling_Channels_mesh.msh]: ") or 'meshs/Cooling_Channels_mesh.msh'
    out_dir = input("Output directory [generated_project]: ") or 'generated_project'
    try:
        frac = float(input("Fraction of pi to study (e.g., 0.5 for half-pi) [0.5]: ") or 0.5)
    except ValueError:
        frac = 0.5
    config_path = input("Path to config.yaml [config.yaml]: ") or 'config.yaml'
    combustion_choice = input("Enable combustion (reacting flow)? [y/N]: ").strip().lower()
    combustion = combustion_choice == 'y'
    # Pass combustion as an override to the config
    generate_project(mesh_files, out_dir, fraction_of_pi=frac, config_path=config_path, combustion=combustion)

def validate_generated_project(output_dir, mesh_files):
    """
    Validate the generated project for:
    1. Missing required files
    2. Unreplaced placeholders
    3. Mesh/interface consistency
    """
    import fnmatch
    errors = []
    # 1. Check for required files
    required_files = [
        'calculix/nozzle.inp',
        'openfoam/interior/mesh.msh',
        'openfoam/exterior/mesh.msh',
        'openfoam/cooling_channel/mesh.msh',
        'precice/precice-config.xml',
        'run_all.sh',
        'clean_all.sh',
        'README.md',
    ]
    for f in required_files:
        if not os.path.isfile(os.path.join(output_dir, f)):
            errors.append(f"Missing required file: {f}")
    # 2. Scan for unreplaced placeholders
    for root, _, files in os.walk(output_dir):
        for file in files:
            if fnmatch.fnmatch(file, '*.msh'):
                continue  # skip mesh files
            path = os.path.join(root, file)
            with open(path, 'r', errors='ignore') as f:
                content = f.read()
                if re.search(r'\{\{.*?\}\}', content):
                    errors.append(f"Unreplaced placeholder in {path}")
    # 3. Mesh/interface consistency (example: check PreCICE XML for interface names)
    precice_xml = os.path.join(output_dir, 'precice/precice-config.xml')
    if os.path.isfile(precice_xml):
        with open(precice_xml, 'r') as f:
            xml_content = f.read()
        # Find all interface names in XML (e.g., <mesh name="...">)
        interface_names = re.findall(r'<mesh name="([^"]+)"', xml_content)
        # Check that these names exist in at least one mesh physical name
        mesh_phys_names = []
        for mesh_path in mesh_files.values():
            mesh_phys_names.extend(parse_physical_names(mesh_path).values())
        for name in interface_names:
            if name not in mesh_phys_names:
                errors.append(f"Interface '{name}' in PreCICE XML not found in any mesh physical names.")
    if errors:
        print("\nVALIDATION ERRORS DETECTED:")
        for err in errors:
            print("-", err)
        print("\nPlease fix the above issues before running the simulation.")
    else:
        print("\nValidation successful: All required files and interfaces are present, and no unreplaced placeholders found.")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == '--wizard':
        cli_wizard()
    else:
        # Automatically detect mesh files in the meshs/ directory
        mesh_files = {
            'solid': 'meshs/Solid_mesh.msh',
            'interior_fluid': 'meshs/Inner_Fluid_mesh.msh',
            'exterior_fluid': 'meshs/Outer_Fluid_mesh.msh',
            'cooling_channel_fluid': 'meshs/Cooling_Channels_mesh.msh',
        }
        generate_project(mesh_files, 'generated_project', fraction_of_pi=0.5)
        validate_generated_project('generated_project', mesh_files)
