#!/bin/bash
#ex running from pdb dir: ./../code/separate.sh "5p9j.pdb" "394:659" "701"

set -e 
pdb=$1 #"5p9j.pdb"
prot=$2 #"394:659"
lig=$3 #"701"
pdb_selres -$prot $pdb | pdb_keepcoord | pdb_tidy | pdb_reatom | pdb_reres > prot.pdb
pdb_selres -$lig $pdb | pdb_keepcoord | pdb_tidy | pdb_reatom | pdb_reres > lig.pdb
#may still need to do selchain if there are replicate chains for the same ligand or something
