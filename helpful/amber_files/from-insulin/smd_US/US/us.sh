#!/bin/bash
#SBATCH --mail-user=kyleghaby@uchicago.edu # Who to send emails to 
#SBATCH --mail-type=ALL # Send emails on start, end and failure 
#SBATCH --job-name=us # Name to show in the job queue 
#SBATCH --mem=50000M
#SBATCH --ntasks=60 # Total number of mpi tasks requested
#SBATCH --nodes=3
#SBATCH --time=170:00:00
##SBATCH --gres=gpu:1                     # Include GPU generic resource
##SBATCH --partition=gpu
##SBATCH --qos=debug
set -e 

module purge
module load amber/18-gcc-6.2.0-410.79
module load plumed/2.6.0-gcc-6.2.0-openmpi-3.1.3 

cd ../smd
./getrestarts.exe #get restarts from smd sim
cd ../US

for i in `seq 1.65 .1 3.65`;do
mkdir -p US_$i
cd US_$i
cp ../us.mdin .
cp ../../../../../../tleap/sys.parm7 .
cp ../../smd/restarts/$i.rst7 .
cat >plumed.dat <<EOF
#set up two variables
#GROUP ATOMS=1-762 LABEL=g1
#GROUP ATOMS=763-1524 LABEL=g2
COM ATOMS=1-762 LABEL=com1
COM ATOMS=763-1524 LABEL=com2
dist: DISTANCE ATOMS=com1,com2 NOPBC 
restraint-dist: RESTRAINT ARG=dist KAPPA=10 AT=$i

PRINT STRIDE=1 ARG=dist.*,restraint-dist.bias FILE=COLVAR

EOF
mpirun -n 60 pmemd.MPI -O -i us.mdin -o us.out -p sys.parm7 -c $i.rst7 -x us.nc

/scratch/ksg225/analysis_scripts/histogram -i COLVAR -col 2  -o COLVAR.histo -int .01

cd ..
echo " US_$i completed"
done
