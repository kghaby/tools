#!/bin/bash
set -e 

#paths are from perspective of prod dir 
jobname_base="test"
parm="../prep/BTK1_IB_l.parm7"
prev_slurmID="1" #dependency ID
prev_rst="../equil/equil.5.rst7" #equil if new prod
prod_range=(1 100) #2 object array. first and last. each prod is 20 ns 
time_var="48:00:00"


#FYI: 10 prod runs are made per slurm job
maxprodperslurm=10

#get slurm blocks from prod range
first=${prod_range[0]}
last=${prod_range[1]}
amountprods=$(echo "($last+1)-$first" | bc)
amountjobs=$(echo "(($amountprods-1)/$maxprodperslurm)+1" | bc)
echo "Making $amountjobs slurm jobs that will run $amountprods prod cycles."

i=$first
j=$(echo "$first+9" | bc)

for x in `seq 1 1 $amountjobs` 
do

#check if block is last block and needs to be smaller than 10 cycles
if [ $j -gt $last ]; then
j=$last
fi

#make slurm file
echo "#!/bin/bash
#SBATCH --dependency=$prev_slurmID
#SBATCH --mail-user=kyleghaby@uchicago.edu # Who to send emails to
#SBATCH --mail-type=ALL # Send emails on start, end and failure
#SBATCH --job-name=${jobname_base}.$i-$j
#SBATCH --time=$time_var
#SBATCH --account=pi-roux
#SBATCH --partition=beagle3
#SBATCH --gres=gpu:1
#SBATCH --nodes=1
#SBATCH --ntasks=1
##SBATCH --exclude=beagle3-0008,beagle3-0017,beagle-0028,beagle-0029
set -e 
module unload amber
module load amber

parm=$parm
prev_rst=$prev_rst

for a in {$i..$j}
do
pmemd.cuda -O -i prod.mdin -o prod.\$a.mdout -p \$parm -c \$prev_rst -r prod.\$a.rst7 -x prod.\$a.nc -inf prod.\$a.mdinfo
prev_rst=prod.\$a.rst7	   
done
" > prod.$i-$j.slurm

RES=$(sbatch prod.$i-$j.slurm)
echo "Submitted prod.$i-$j.slurm, and the id is: ${RES##* }"

prev_rst="prod.$j.rst7"
prev_slurmID=${RES##* }
i=$(echo "$j+1" | bc)
j=$(echo "$i+9" | bc)
done
