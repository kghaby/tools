#!/bin/bash
#need to tailor atom groups and i seq for system of interest

#cd ../smd
#./getrestarts.exe #get restarts from smd sim
#cd ../US

for i in `seq 1.65 .1 3.65`;do
mkdir -p US_$i
cd US_$i
echo "#!/bin/bash
#SBATCH --mail-user=kyleghaby@uchicago.edu # Who to send emails to 
#SBATCH --mail-type=ALL # Send emails on start, end and failure 
#SBATCH --job-name=us_$i # Name to show in the job queue 
#SBATCH --mem=60000M
#SBATCH --exclude=cn[1],cn[6]
#SBATCH --ntasks=60 # Total number of mpi tasks requested
#SBATCH --nodes=3
#SBATCH --time=090:00:00
##SBATCH --gres=gpu:1                     # Include GPU generic resource
##SBATCH --partition=gpu
##SBATCH --qos=debug
set -e 

module purge
module load amber/18-gcc-6.2.0-410.79
module load plumed/2.6.0-gcc-6.2.0-openmpi-3.1.3 


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
restraint-dist: RESTRAINT ARG=dist KAPPA=500 AT=$i

PRINT STRIDE=10 ARG=dist.*,restraint-dist.bias FILE=COLVAR

EOF

mpirun -n 60 pmemd.MPI -O -i us.mdin -o us.1.out -p sys.parm7 -c $i.rst7 -r us.1.rst7 -x us.1.nc
for a in {2..10}
	do
		b=\$((a-1))
		mpirun -n 60 pmemd.MPI -O -i us.mdin -o us.\$a.out -p sys.parm7 -c us.\$b.rst7 -r us.\$a.rst7 -x us.\$a.nc
	done

/scratch/ksg225/analysis_scripts/histogram -i bck.0.COLVAR -col 2  -o COLVAR.1.histo -int .01
/scratch/ksg225/analysis_scripts/histogram -i bck.1.COLVAR -col 2  -o COLVAR.2.histo -int .01
/scratch/ksg225/analysis_scripts/histogram -i bck.2.COLVAR -col 2  -o COLVAR.3.histo -int .01
/scratch/ksg225/analysis_scripts/histogram -i bck.3.COLVAR -col 2  -o COLVAR.4.histo -int .01
/scratch/ksg225/analysis_scripts/histogram -i bck.4.COLVAR -col 2  -o COLVAR.5.histo -int .01
/scratch/ksg225/analysis_scripts/histogram -i bck.5.COLVAR -col 2  -o COLVAR.6.histo -int .01
/scratch/ksg225/analysis_scripts/histogram -i bck.6.COLVAR -col 2  -o COLVAR.7.histo -int .01
/scratch/ksg225/analysis_scripts/histogram -i bck.7.COLVAR -col 2  -o COLVAR.8.histo -int .01
/scratch/ksg225/analysis_scripts/histogram -i bck.8.COLVAR -col 2  -o COLVAR.9.histo -int .01
/scratch/ksg225/analysis_scripts/histogram -i COLVAR -col 2  -o COLVAR.10.histo -int .01
 
" > us_$i.sh
sbatch us_$i.sh
echo "us_$i.sh submitted"
cd ..
done