#!/bin/bash
#SBATCH --job-name=min
#SBATCH --time=00:30:00
#SBATCH --partition=beagle3
#SBATCH --account=pi-roux
#SBATCH --gres=gpu:1
#SBATCH --nodes=1
#SBATCH --ntasks=1

module unload amber
module load amber
parm="../prep/MKK7_IB_l.parm7"
rst="../prep/MKK7_IB_l.rst7"
pmemd.cuda -O -i minim.mdin -p $parm -c $rst -o minim.mdout -r minim.rst7 -x minim.nc -inf minim.mdinfo -ref $rst 

