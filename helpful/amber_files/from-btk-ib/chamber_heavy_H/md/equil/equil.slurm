#!/bin/bash
#SBATCH --job-name=equil
##SBATCH --output=equil.out
##SBATCH --error=equil.err
#SBATCH --time=12:00:00
#SBATCH --partition=rouxgpu
#SBATCH --qos=roux
#SBATCH --gres=gpu:1
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --constraint=gtx780
#SBATCH --nodelist=midway-l12b-02

module unload amber
module load amber

pmemd.cuda -O -i equil.mdin -p ../../build/system.parm7 -c ../min/minim.rst7 -o equil.mdout -r equil.rst7 -inf equil.mdinfo -ref ../../build/system.rst7 -x equil.nc
