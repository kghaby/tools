#!/bin/bash
#SBATCH --mail-user=kyleghaby@uchicago.edu       # Who to send emails to
#SBATCH --mail-type=ALL                  # Send emails on start, end and failure
#SBATCH --job-name=min                # Name to show in the job queue
#SBATCH --mem=500M
#SBATCH --ntasks=20                      # Total number of mpi tasks requested
#SBATCH --nodes=1                        # Total number of nodes requested
#SBATCH --time=00:02:00

module purge
module load amber


mpirun -np 20 pmemd.MPI -O -i min2.in -o min.out -p sys.parm7 -c sys.rst7 -r min.rst7



