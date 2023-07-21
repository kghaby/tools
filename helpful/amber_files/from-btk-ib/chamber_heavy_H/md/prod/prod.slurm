#!/bin/bash
#SBATCH --mail-user=kyleghaby@uchicago.edu # Who to send emails to
#SBATCH --mail-type=ALL # Send emails on start, end and failure
#SBATCH --job-name=checkconv
##SBATCH --output=prod.out
##SBATCH --error=prod.err
#SBATCH --time=24:00:00
#SBATCH --partition=rouxgpu
#SBATCH --qos=roux
#SBATCH --gres=gpu:1
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --constraint=gtx780
#SBATCH --nodelist=midway-l12b-02 
##SBATCH --exclude=midway-l12b-08,midway-l12b-11,midway-l13b-05,midway-l12b-02

module unload amber
module load amber

pmemd.cuda -O -i prod.mdin -p ../../build/system.parm7 -c ../equil/equil.rst7 -o prod.mdout -r prod.rst7 -inf prod.mdinfo -x prod.nc
