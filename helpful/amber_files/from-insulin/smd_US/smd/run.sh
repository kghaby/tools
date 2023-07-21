#!/bin/bash
#SBATCH --mail-user=kyleghaby@uchicago.edu # Who to send emails to 
#SBATCH --mail-type=ALL # Send emails on start, end and failure 
#SBATCH --job-name=smd # Name to show in the job queue 
#SBATCH --mem=600M
#SBATCH --ntasks=1 # Total number of mpi tasks requested
#SBATCH --nodes=1
#SBATCH --gres=gpu:1                     # Include GPU generic resource
#SBATCH --partition=gpu                  # Partition (a.k.a. queue) to use
#SBATCH --time=80:00:00
set -e 

module purge
module load amber 

cd smd
pmemd.cuda -O -p  ../../../../../tleap/sys.parm7 -c ../../prod.100.rst7 -i smd.mdin -x smd.nc -o smd.out -inf smd.mdinfo -r smd.rst7 -l smd.log

cd ..
