#!/bin/bash
#SBATCH --mail-user=kyleghaby@uchicago.edu       # Who to send emails to
#SBATCH --mail-type=ALL                  # Send emails on start, end and failure
#SBATCH --job-name=equil                # Name to show in the job queue
#SBATCH --mem=900M
#SBATCH --ntasks=20                      # Total number of mpi tasks requested
#SBATCH --nodes=1                        # Total number of nodes requested
#SBATCH --time=00:30:00

module purge 
module load amber


mpirun -n 20 pmemd.MPI -O -i equil.1.in -o equil.1.out -p sys.parm7 -c ../2-heat/heat.2.rst7 -r equil.1.rst7 -ref ../2-heat/heat.2.rst7 -x equil.1.nc

for a in {2..5}
   do
      b=$((a-1))
      mpirun -n 20 pmemd.MPI -O -i equil.$a.in -o equil.$a.out -p sys.parm7 -c equil.$b.rst7 -r equil.$a.rst7 -x equil.$a.nc -ref equil.$b.rst7
   done



