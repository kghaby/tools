#!/bin/bash 
set -ea


cpptraj -i rmsd_l_refx.traj
cpptraj -i rmsd_u_refx.traj

cpptraj -i rmsd_l_refl.traj
cpptraj -i rmsd_u_refl.traj

# wham

# plot

