#!/bin/bash
#SBATCH --mail-user=kyleghaby@uchicago.edu # Who to send emails to 
#SBATCH --mail-type=FAIL # Send emails on start, end and failure 
#SBATCH --job-name=3.4US46l # Name to show in the job queue 
#SBATCH --ntasks=1 # Total number of mpi tasks requested
#SBATCH --nodes=1
#SBATCH --time=48:00:00
#SBATCH --gres=gpu:1                     # Include GPU generic resource
#SBATCH --account=pi-roux
#SBATCH --partition=beagle3

module load amber

mv -n dihed_46.dat dihed_46.0.dat
mv -n dihed_46.histo dihed_46.0.histo  

pmemd.cuda -O -i US_46.mdin -o US_46.1.mdout -p ../../prep/BTK_IB_l_nobadwater.parm7 -c ../../../../md_3/linked/US_1/US_46/US_46.20.rst7 -r US_46.1.rst7 -x US_46.1.nc -inf US_46.1.mdinfo
mv dihed_46.dat dihed_46.1.dat
./../histogram -i dihed_46.1.dat -col 2  -o dihed_46.1.histo -int .1

for a in {2..20}
   do
      b=$((a-1))
      pmemd.cuda -O -i US_46.mdin -o US_46.$a.mdout -p ../../prep/BTK_IB_l_nobadwater.parm7 -c US_46.$b.rst7 -r US_46.$a.rst7 -x US_46.$a.nc -inf US_46.$a.mdinfo
      mv dihed_46.dat dihed_46.$a.dat
      ./../histogram -i dihed_46.$a.dat -col 2  -o dihed_46.$a.histo -int .1
   done

