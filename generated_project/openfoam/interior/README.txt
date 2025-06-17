/* OpenFOAM interior fluid case template */
/* Mesh file: {{MESH_PATH}} */
/* Fraction of pi: {{FRACTION_OF_PI}} */

/* Replace this file with a real OpenFOAM case template for the interior fluid region. */

/* Example: system/controlDict, constant/transportProperties, 0/U, etc. */

system/controlDict:
application     rhoCentralFoam;
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
        molWeight       28.96;
    }
    thermodynamics
    {
        Cp              1005;
        Hf              0;
    }
    transport
    {
        mu              1.8e-05;
        Pr              0.7;
    }
}

constant/boundaryConditions:
// Inlet: total pressure, total temperature
// Outlet: fixed pressure
// Wall: coupled to solid via PreCICE

0/U:
// Initial velocity field

0/p:
// Initial pressure field

preciceDict:
participantName   OpenFOAM-interior;
meshName          INTERIOR_MESH;
writeInterval     1;

// PreCICE boundary patches: nozzleWall
