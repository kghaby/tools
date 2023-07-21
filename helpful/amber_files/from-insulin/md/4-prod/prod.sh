#!/bin/bash 
#SBATCH --mail-user=kyleghaby@uchicago.edu # Who to send emails to 
#SBATCH --mail-type=ALL # Send emails on start, end and failure 
#SBATCH --job-name=prod # Name to show in the job queue 
#SBATCH --ntasks=1 # Total number of mpi tasks requested
#SBATCH --nodes=1 # Total number of nodes requested
#SBATCH --mem=400M
#SBATCH --gres=gpu:1                     # Include GPU generic resource
#SBATCH --partition=gpu                  # Partition (a.k.a. queue) to use
#SBATCH --time=105:00:00

module purge
module load amber

pmemd.cuda -O -i prod.in -o prod.1.out -p sys.parm7 -c ../3-equil/equil.5.rst7 -r prod.1.rst7 -x prod.1.nc

for a in {2..100}
   do
      b=$((a-1))
      pmemd.cuda -O -i prod.in -o prod.$a.out -p sys.parm7 -c prod.$b.rst7 -r prod.$a.rst7 -x prod.$a.nc
   done

