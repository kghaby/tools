#!/bin/bash 
set -ea

# hist
../../../../../code/general_analysis/histogram -i rmsd_l_refx_lig.dat -col 2  -o rmsd_l_refx_lig.histo -int .01
../../../../../code/general_analysis/histogram -i rmsd_u_refx_lig.dat -col 2  -o rmsd_u_refx_lig.histo -int .01
../../../../../code/general_analysis/histogram -i rmsd_l_refl_lig.dat -col 2  -o rmsd_l_refl_lig.histo -int .01
../../../../../code/general_analysis/histogram -i rmsd_u_refl_lig.dat -col 2  -o rmsd_u_refl_lig.histo -int .01

#wham
#T="303.15"

#wham 0 5 1000 0.01 $T 0 rmsd_u_refx_lig_meta.dat rmsd_u_refx_lig_FE.dat

