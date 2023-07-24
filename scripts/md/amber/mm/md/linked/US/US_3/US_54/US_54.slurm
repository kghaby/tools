#!/bin/bash
#SBATCH --dependency=afterok:3603586
#SBATCH --mail-user=kyleghaby@uchicago.edu # Who to send emails to 
##SBATCH --mail-type=ALL # Send emails on start, end and failure 
#SBATCH --job-name=US_54_2 # Name to show in the job queue 
#SBATCH --ntasks=1 # Total number of mpi tasks requested
#SBATCH --nodes=1
#SBATCH --time=48:00:00
#SBATCH --gres=gpu:1                     # Include GPU generic resource
#SBATCH --account=pi-roux
#SBATCH --partition=beagle3

module load amber

./../get_frame.sh 50 54

pmemd.cuda -O -i US_54.mdin -o US_54.mdout -p ../../prep/BTK_IB_l_nobadwater.parm7 -c for_cv_54.rst7 -r US_54.rst7 -x US_54.nc -inf US_54.mdinfo

cpptraj -i pseudodihedral.traj

./../histogram -i dihed_54.dat -col 2  -o dihed_54.histo -int .01
 

