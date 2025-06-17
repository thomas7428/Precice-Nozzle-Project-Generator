/* OpenFOAM cooling channel fluid case template */
/* Mesh file: generated_project/meshs/Solid_mesh.msh */
/* Fraction of pi: 0.5 */

/* Replace this file with a real OpenFOAM case template for the cooling channel fluid region. */

/* Example: system/controlDict, constant/transportProperties, 0/U, etc. */

system/controlDict:
application     icoFoam;
startFrom       startTime;
endTime         0.01;
deltaT          1e-6;
writeControl    timeStep;
writeInterval   100;

constant/thermophysicalProperties:
thermoType
{
    type            heRhoThermo;
    mixture         pureMixture;
    transport       sutherland;
    thermo          hConst;
    equationOfState perfectGas;
    specie          specie;
    energy          sensibleEnthalpy;
}
mixture
{
    specie
    {
        nMoles          1;
        molWeight       18.02;
    }
    thermodynamics
    {
        Cp              4182;
        Hf              0;
    }
    transport
    {
        mu              1.0e-03;
        Pr              7.0;
    }
}

constant/boundaryConditions:
// Inlet: fixed mass flow, fixed temperature
// Outlet: fixed pressure
// Wall: coupled to solid via PreCICE (cooling channel wall)

0/U:
// Initial velocity field

0/p:
// Initial pressure field

preciceDict:
participantName   OpenFOAM-cooling;
meshName          COOLING_MESH;
writeInterval     1;

// PreCICE boundary patches: coolingWall
