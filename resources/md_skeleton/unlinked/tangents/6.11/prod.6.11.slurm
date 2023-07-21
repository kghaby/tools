#!/bin/bash
#SBATCH --dependency=3604849
#SBATCH --mail-user=kyleghaby@uchicago.edu # Who to send emails to
#SBATCH --mail-type=ALL # Send emails on start, end and failure
#SBATCH --job-name=p6.11_u
##SBATCH --output=prod.out
##SBATCH --error=prod.err
#SBATCH --time=48:00:00
#SBATCH --account=pi-roux 
#SBATCH --partition=beagle3
##SBATCH --qos=beagle3
#SBATCH --gres=gpu:1
#SBATCH --nodes=1
#SBATCH --ntasks=1
##SBATCH --constraint=gtx780
##SBATCH --nodelist=midway-l12b-02 
##SBATCH --exclude=midway-l12b-08,midway-l12b-11,midway-l13b-05,midway-l12b-02

module unload amber
module load amber

a="6.11"
pmemd.cuda -O -i prod.$a.mdin -p ../../prep/BTK_IB_u_nobadwater.parm7 -c equil.$a.rst7 -o prod.$a.mdout -r prod.$a.rst7 -inf prod.$a.mdinfo -x prod.$a.nc

