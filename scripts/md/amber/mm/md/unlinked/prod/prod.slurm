#!/bin/bash
#SBATCH --dependency=3919835
#SBATCH --mail-user=kyleghaby@uchicago.edu # Who to send emails to
#SBATCH --mail-type=ALL # Send emails on start, end and failure
#SBATCH --job-name=p_u
#SBATCH --time=48:00:00
#SBATCH --account=pi-roux 
#SBATCH --partition=beagle3
#SBATCH --gres=gpu:1
#SBATCH --nodes=1
#SBATCH --ntasks=1

module unload amber
module load amber

parm="../prep/MKK7_IB_u.parm7"

pmemd.cuda -O -i prod.mdin -p $parm -c ../equil/equil.5.rst7 -o prod.1.mdout -r prod.1.rst7 -inf prod.1.mdinfo -x prod.1.nc

for a in {2..10}
   do
      b=$((a-1))
      pmemd.cuda -O -i prod.mdin -o prod.$a.mdout -p $parm -c prod.$b.rst7 -r prod.$a.rst7 -x prod.$a.nc -inf prod.$a.mdinfo
   done

