#!/bin/bash
#SBATCH --job-name=min
##SBATCH --output=equil.out
##SBATCH --error=equil.err
#SBATCH --time=12:00:00
#SBATCH --partition=rouxgpu
#SBATCH --qos=roux
#SBATCH --gres=gpu:1
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --constraint=gtx780

module unload amber
module load amber

pmemd.cuda -O -i minim.mdin -p ../../build/system.parm7 -c ../../build/system.rst7 -o minim.mdout -r minim.rst7 -inf minim.mdinfo -ref ../../build/system.rst7
