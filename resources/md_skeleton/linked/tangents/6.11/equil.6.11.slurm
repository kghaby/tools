#!/bin/bash
#SBATCH --job-name=e6.11
##SBATCH --output=equil.out
##SBATCH --error=equil.err
#SBATCH --time=48:00:00
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

a="6.11"
pmemd.cuda -O -i equil.$a.mdin -o equil.$a.mdout -p ../../prep/BTK_IB_l_nobadwater.parm7 -c  ../../equil/equil.5.rst7 -r equil.$a.rst7 -ref ../../prep/BTK_IB_l_nobadwater.rst7 -x equil.$a.nc -inf equil.$a.mdinfo


                                                                                                      
