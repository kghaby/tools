#!/bin/bash 
set -ea

#setup
./rmsd_setup.sh

cpptraj -i rmsd_l_refx.traj
cpptraj -i rmsd_u_refx.traj

cpptraj -i rmsd_l_refl.traj
cpptraj -i rmsd_u_refl.traj

# hist
../../../../../../code/histogram -i rmsd_l_refx_lig.dat -col 2  -o rmsd_l_refx_lig.histo -int .05
../../../../../../code/histogram -i rmsd_u_refx_lig.dat -col 2  -o rmsd_u_refx_lig.histo -int .05
../../../../../../code/histogram -i rmsd_l_refl_lig.dat -col 2  -o rmsd_l_refl_lig.histo -int .05
../../../../../../code/histogram -i rmsd_u_refl_lig.dat -col 2  -o rmsd_u_refl_lig.histo -int .05
  

# wham

# plot
./plot_rmsd.sh
./plot_histo.sh
