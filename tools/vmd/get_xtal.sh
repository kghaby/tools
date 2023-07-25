#!/bin/bash
set -ea

pdbid=$1

############

mkdir -p xtal
cd xtal

pdbf="${pdbid}.pdb"

#fetch
pdb_fetch -biounit $pdbid > $pdbf

#reres
pdb_reres $pdbf > ${pdbid}_reres.pdb
pdbf_reres="${pdbid}_reres.pdb"

#vmd format
cat > vmdpdb.tcl <<EOF
mol addfile $pdbf_reres
[atomselect top "altloc \"\" or altloc \"A\""] writepdb ${pdbid}_reres_noaltloc.pdb
exit
EOF

vmd -dispdev text -e vmdpdb.tcl

cd ..

