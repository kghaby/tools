#!/bin/bash
#SBATCH --mail-user=kyleghaby@uchicago.edu # Who to send emails to 
#SBATCH --mail-type=FAIL # Send emails on start, end and failure 
#SBATCH --job-name=3.4US106l # Name to show in the job queue 
#SBATCH --ntasks=1 # Total number of mpi tasks requested
#SBATCH --nodes=1
#SBATCH --time=48:00:00
#SBATCH --gres=gpu:1                     # Include GPU generic resource
#SBATCH --account=pi-roux
#SBATCH --partition=beagle3

module load amber

mv -n dihed_106.dat dihed_106.0.dat
mv -n dihed_106.histo dihed_106.0.histo  

pmemd.cuda -O -i US_106.mdin -o US_106.1.mdout -p ../../prep/BTK_IB_l_nobadwater.parm7 -c ../../../../md_3/linked/US_1/US_106/US_106.20.rst7 -r US_106.1.rst7 -x US_106.1.nc -inf US_106.1.mdinfo
mv dihed_106.dat dihed_106.1.dat
./../histogram -i dihed_106.1.dat -col 2  -o dihed_106.1.histo -int .1

for a in {2..20}
   do
      b=$((a-1))
      pmemd.cuda -O -i US_106.mdin -o US_106.$a.mdout -p ../../prep/BTK_IB_l_nobadwater.parm7 -c US_106.$b.rst7 -r US_106.$a.rst7 -x US_106.$a.nc -inf US_106.$a.mdinfo
      mv dihed_106.dat dihed_106.$a.dat
      ./../histogram -i dihed_106.$a.dat -col 2  -o dihed_106.$a.histo -int .1
   done

