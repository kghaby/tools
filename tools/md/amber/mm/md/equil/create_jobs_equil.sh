#!/bin/bash
set -e 

#paths are from perspective of prod dir 
jobname_base="test"
parm="../prep/BTK1_IB_l.parm7"
prev_slurmID="1" #put as 1 if it isnt needed
prev_rst="../minim/minim.rst7" #min if new equil
restraint_arr=(10.0 5.0 2.5 1.0 0.5) #arr for npt-sim restraints 
time_var="10:00:00"
restraint_mask='(:1-266)&(@CA,C,O,N)|(:IB&!@H=)|((:IB<:10)&(:268-442&!@H=))'
xtalref="../prep/BTK1_IB_l.rst7"



first=0 #start with equil.0.mdin
last=${#restraint_arr[@]} #end with equil.$last.mdin


#make nvt mdin
echo "Equil
 &cntrl
    imin=0,
    irest=0,       ! This is NOT a restart of an old MD simulation
    ntx=1,         ! So our inpcrd file has no velocities

    ! Temperature control
    ntt=3,         ! Langevin dynamics
    gamma_ln=1.0,  ! Friction coefficient (ps^-1)
    tempi=310,   ! Initial temp -- give it some small random velocities
    temp0=310,   ! Target temperature

    ! Potential energy control
    cut=12.0,       ! nonbonded cutoff, in Angstroms
    fswitch=10.0,   ! Force-based switching

    !SHAKE
    ntc=2,
    ntf=2,

    ntpr=1000,     ! Print energies every 1000 steps
    ntwx=1000,     ! Print coordinates every 1000 steps to the trajectory
    ntwr=10000,    ! Print a restart file every 10K steps
    nstlim=25000, ! Number of MD steps
    ioutfm=1,  ! netcdf format
    ntxo=2,        ! Write NetCDF format

    dt=0.001,
    iwrap = 0, ! dont wrap

    ! restraints
    ntr=1,
    restraint_wt=10.0, !units: kcal/mol/Ang^2
    restraintmask='$restraint_mask', !mask

    ! Set water atom/residue names for SETTLE recognition
    watnam='WAT',  ! Water residues names. Usually WAT or TIP3
    owtnm='O',     ! Water oxygens names. Usually O or OH2
 /
 &ewald
    vdwmeth = 0,
 &end
/
" > equil.0.mdin

#make npt mdin
i=1
for restraint in "${restraint_arr[@]}"
do
echo "Equil
 &cntrl
    imin=0,
    irest=1,       ! This is a restart of an old MD simulation
    ntx=5,         ! So our inpcrd file has velocities

    !SHAKE
    ntc=2,
    ntf=2,

    ! Temperature control
    ntt=3,         ! Langevin dynamics
    gamma_ln=1.0,  ! Friction coefficient (ps^-1)
    temp0=310,   ! Target temperature

  ! Potential energy control
    cut=12.0,       ! nonbonded cutoff, in Angstroms
    fswitch=10.0,   ! Force-based switching
    
    ntc=2,
    ntf=2,
    ig=-1,
    ntpr=10000,     ! Print energies every 10000 steps
    ntwx=10000,     ! Print coordinates every 10000 steps to the trajectory
    ntwr=100000,    ! Print a restart file every 100K steps
    nstlim=1000000, ! Number of MD steps
    ioutfm=1,  ! netcdf format
    dt=0.002,
    iwrap = 0, ! wrap coords for long sim so coordinate output doesnt overflow

    ntb=2,        ! Constant pressure periodic boundary conditions
    ntp=1,        ! isotropic pressure coupling
    taup=1.0,     ! Pressure relaxation time (ps)
    barostat=2,   ! Monte Carlo barostat
    ntxo=2,
    ntr=1,
    restraint_wt=$restraint, !units: kcal/mol/Ang^2
    restraintmask='$restraint_mask', !mask
    ! Set water atom/residue names for SETTLE recognition
    watnam='WAT',  ! Water residues names. Usually WAT or TIP3
    owtnm='O',     ! Water oxygens names. Usually O or OH2
 /
 &ewald
    vdwmeth = 0,
 &end
/
" > equil.$i.mdin
i=$(($i+1))
done

#make slurm file
echo "#!/bin/bash
#SBATCH --dependency=$prev_slurmID
#SBATCH --mail-user=kyleghaby@uchicago.edu # Who to send emails to
#SBATCH --mail-type=ALL # Send emails on start, end and failure
#SBATCH --job-name=${jobname_base}
#SBATCH --time=$time_var
#SBATCH --account=pi-roux
#SBATCH --partition=beagle3
#SBATCH --gres=gpu:1
#SBATCH --nodes=1
#SBATCH --ntasks=1
##SBATCH --exclude=beagle3-0008,beagle3-0017,beagle-0028,beagle-0029
module unload amber
module load amber

parm="$parm"
prev_rst="$prev_rst"
xtalref="$xtalref"

for a in {$first..$last}
do
pmemd.cuda -O -i equil.\$a.mdin -o equil.\$a.mdout -p \$parm -c \$prev_rst -r equil.\$a.rst7 -x equil.\$a.nc -inf equil.\$a.mdinfo -ref \$xtalref
prev_rst=equil.\$a.rst7	   
done
" > equil.slurm

RES=$(sbatch equil.slurm)
echo "Submitted equil.slurm, and the id is: ${RES##* }"

