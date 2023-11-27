#!/bin/bash
set -e 

#paths are from perspective of prod dir 
jobname_base="minim"
parm="../prep/EGFR_AB_l.parm7"
prev_rst="../prep/EGFR_AB_l.rst7" #xtal rst if new system
time_var="00:30:00"
restraint_mask='(:1-321)&(@CA,C,O,N)|(:AB&!@H=)|((:AB<:10)&(:323-348&!@H=))'
xtalref="$prev_rst"




#make nvt mdin
echo "Minimization
 &cntrl
    ! Minimization options
    imin=1,        ! Turn on minimization
    maxcyc=5000,   ! Maximum number of minimization cycles
    ncyc=2500,     !  steepest-descent steps, better for strained systems

    ! Potential energy function options
    cut=12.0,      ! nonbonded cutoff, in Angstroms
    fswitch=10.0,  ! Force-based switching

    ! Control how often information is printed to the output file
    ntpr=100,      ! Print energies every 100 steps
    ntxo=2,        ! Write NetCDF format
    ntwx=100,     ! write coordinates after this many steps

    ! Restraint options
    ntr=1,         ! Positional restraints for proteins, sugars, and ligands
    restraint_wt=1.0, !units: kcal/mol/Ang^2
    restraintmask='$restraint_mask', !mask

    ! Set water atom/residue names for SETTLE recognition
    watnam='WAT',  ! Water residues are named WAT
    owtnm='O',     ! Water oxygens are named O
 /

 &ewald
    vdwmeth = 0,
 &end
/

" > minim.mdin


#make slurm file
echo "#!/bin/bash
#SBATCH --mail-user=kyleghaby@uchicago.edu # Who to send emails to
#SBATCH --mail-type=ALL # Send emails on start, end and failure
#SBATCH --job-name=${jobname_base}
#SBATCH --time=$time_var
#SBATCH --account=pi-roux
#SBATCH --partition=beagle3
#SBATCH --gres=gpu:1
#SBATCH --nodes=1
#SBATCH --ntasks=1
##SBATCH --exclude=beagle3-0008,beagle3-0017,beagle3--0027,beagle3-0028,beagle3-0029,beagle3--0030
module unload amber
module load amber

parm="$parm"
prev_rst="$prev_rst"
xtalref="$xtalref"

pmemd.cuda -O -i minim.mdin -o minim.mdout -p \$parm -c \$prev_rst -r minim.rst7 -x minim.nc -inf minim.mdinfo -ref \$xtalref
" > minim.slurm

RES=$(sbatch minim.slurm)
echo "Submitted minim.slurm, and the id is: ${RES##* }"

