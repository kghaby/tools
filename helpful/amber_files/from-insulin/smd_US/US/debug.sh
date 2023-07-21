#!/bin/bash
#SBATCH --mail-user=ksg225@nau.edu # Who to send emails to 
#SBATCH --mail-type=ALL # Send emails on start, end and failure 
#SBATCH --job-name=debug46.5 # Name to show in the job queue 
#SBATCH --mem=6000M
#SBATCH --ntasks=60 # Total number of mpi tasks requested
#SBATCH --nodes=3
#SBATCH --time=000:30:00
##SBATCH --gres=gpu:1                     # Include GPU generic resource
##SBATCH --partition=gpu
##SBATCH --qos=debug
set -e 

module purge
module load amber/18-gcc-6.2.0-410.79
module load plumed/2.6.0-gcc-6.2.0-openmpi-3.1.3 

#this was here to run a min sim before US
#sander.MPI -O -i  -o  -p sys.parm7 -c  -r min.rst

#for i in `seq 40 1 45`;do
mkdir -p US_46.5
cd US_46.5
cp ../debug.mdin .
cp ../../../../../../tleap/sys.parm7 .
cp ../../smd/restarts/6615.rst7 .
cat >plumed.dat <<EOF
#set up two variables
#GROUP ATOMS=1-762 LABEL=g1
#GROUP ATOMS=763-1524 LABEL=g2
COM ATOMS=1-762 LABEL=com1
COM ATOMS=763-1524 LABEL=com2
dist: DISTANCE ATOMS=com1,com2 
restraint-dist: RESTRAINT ARG=dist KAPPA=50 AT=46.5

PRINT STRIDE=1 ARG=dist.*,restraint-dist.bias FILE=COLVAR

EOF
mpirun -n 60 pmemd.MPI -O -i debug.mdin -o us.out -p sys.parm7 -c 6615.rst7 -x us.nc
cd ..
echo " US_$i completed"
done
