#!/usr/bin/env tclsh
# Run: vmd -dispdev text -e path/to/make_vacuum_files.tcl
# Execute from the BFEE/ directory

set basedir [pwd]
set sel_text "not water and not resname POT CLA"

# Strip solvent/ions from ligandOnly.psf/.pdb
mol new ${basedir}/ligandOnly.psf
mol addfile ${basedir}/ligandOnly.pdb waitfor all

set sel [atomselect top $sel_text]
set n [$sel num]
puts "Ligand atoms: $n"

$sel writepsf ${basedir}/ligandOnlyVac.psf
$sel writepdb ${basedir}/ligandOnlyVac.pdb
$sel writexyz ${basedir}/ligandOnlyVac.xyz ;

$sel delete
mol delete all

# Copy ligandOnly .ndx file
file copy -force ${basedir}/ligandOnly.ndx ${basedir}/ligandOnlyVac.ndx

# Strip solvent/ions from fep_ligandOnly.pdb (preserves beta/occupancy FEP flags)
mol new ${basedir}/ligandOnly.psf
mol addfile ${basedir}/fep_ligandOnly.pdb waitfor all

set sel [atomselect top $sel_text]
$sel writepdb ${basedir}/fep_ligandOnlyVac.pdb

$sel delete
mol delete all

puts "Done. Files written:"
puts "  ligandOnlyVac.psf"
puts "  ligandOnlyVac.pdb"
puts "  ligandOnlyVac.xyz"
puts "  ligandOnlyVac.ndx"
puts "  fep_ligandOnlyVac.pdb"

exit
