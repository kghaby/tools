#!/bin/bash
#SBATCH --job-name=de_l
##SBATCH --output=equil.out
##SBATCH --error=equil.err
#SBATCH --time=1:00:00
#SBATCH --account=pi-roux
#SBATCH --partition=beagle3
##SBATCH --qos=beagle3
#SBATCH --gres=gpu:1
#SBATCH --nodes=1
#SBATCH --ntasks=1
##SBATCH --constraint=gtx780
##SBATCH --nodelist=midway-l12b-02

module unload amber
module load amber


pmemd.cuda -O -i debug.mdin -o equil.1.mdout -p ../prep/BTK_IB_l_nobadwater_alt.parm7 -c equil.0.rst7 -r equil.1.rst7 -x equil.1.nc -ref ../prep/BTK_IB_l_nobadwater.rst7 -inf equil.1.mdinfo

                                                                                                      
