#!/bin/bash
#SBATCH --mail-user=kyleghaby@uchicago.edu       # Who to send emails to
#SBATCH --mail-type=ALL                  # Send emails on start, end and failure
#SBATCH --job-name=heat                # Name to show in the job queue
#SBATCH --mem=800M
#SBATCH --ntasks=20                      # Total number of mpi tasks requested
#SBATCH --nodes=1                        # Total number of nodes requested
#SBATCH --time=00:10:00

module purge 
module load amber


mpirun -n 20 pmemd.MPI -O -i heat.1.in -o heat.1.out -p sys.parm7 -c ../1-min/min.rst7 -r heat.1.rst7 -ref ../1-min/min.rst7 -x heat.1.nc
mpirun -n 20 pmemd.MPI -O -i heat.2.in -o heat.2.out -p sys.parm7 -c heat.1.rst7 -r heat.2.rst7 -x heat.2.nc -ref heat.1.rst7



