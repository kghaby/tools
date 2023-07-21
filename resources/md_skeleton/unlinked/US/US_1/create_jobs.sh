#!/bin/bash
#need to tailor atom groups and i seq for system of interest

#paths are from perspective of one deeper from US dir (ie add "../" to path from US dir)
parm="../"
k=200


#make directories and mdin files
for i in `seq -10 4 150`;do
mkdir -p US_$i
cd US_$i
echo "Prod for US_$i
 &cntrl
    imin=0,        ! No minimization
    irest=0,       ! This is not a restart of an old MD simulation
    ntx=1,         ! So our inpcrd file has no velocities

    ! Temperature control
    ntt=3,         ! Langevin dynamics
    gamma_ln=1.0,  ! Friction coefficient (ps^-1)
    temp0=310,   ! Target temperature

    ! Potential energy control
    cut=12.0,      ! nonbonded cutoff, in Angstroms
    fswitch=10.0,  ! Force-based switching

    ! MD settings
    nstlim=5000000, ! _ steps, 10 ns total
    dt=0.002,      ! time step (ps)

    ! SHAKE
    ntc=2,         ! Constrain bonds containing hydrogen
    ntf=2,         ! Do not calculate forces of bonds containing hydrogen

    ! Control how often information is printed
    ntpr=20000,     ! Print energies every _ steps
    ntwx=20000,    ! Print coordinates every _ steps to the trajectory
    ntwr=200000,    ! Print a restart file every _ steps (can be less frequent)
!   ntwv=-1,       ! Uncomment to also print velocities to trajectory
!   ntwf=-1,       ! Uncomment to also print forces to trajectory
    ntxo=2,        ! Write NetCDF format
    ioutfm=1,      ! Write NetCDF format (always do this!)

    ! Wrap coordinates when printing them to the same unit cell
    iwrap=0,

    ! Constant pressure control.
    barostat=2,    ! MC barostat... change to 1 for Berendsen
    ntp=1,         ! 1=isotropic, 2=anisotropic, 3=semi-isotropic w/ surften
    pres0=1.0,     ! Target external pressure, in bar

    ! Set water atom/residue names for SETTLE recognition
    watnam='WAT',  ! Water residues are named WAT
    owtnm='O',    ! Water oxygens are named O
	
	nmropt = 1, ! look for nmr rst
/
 &ewald
    vdwmeth = 0,
 &end
 &wt
  type='DUMPFREQ', istep1=50,
 &end
 &wt 
  type='END',
 &end
DISANG=rst.$i
DUMPAVE=dihed_${i}.dat
" > US_$i.mdin

left=$(echo "$i-180" | bc)
right=$(echo "$i+180" | bc)

echo "Harmonic restraints for $i deg
 &rst
  iat=4352,4347,4357,4362
  r1=$left, r2=$i, r3=$i, r4=$right,
  rk2=${k}, rk3=${k},
 &end
" > rst.$i
cd ..
done


##########
#make slurm files and get frames from prev windows
##########

#do first one
i="-10"
cd US_$i

cat >pseudodihedral.traj <<EOF
parm ../../prep/BTK_IB_u_nobadwater.parm7 
trajin US_$i.nc
dihedral :IB@OAC :IB@CAW :IB@NBF :IB@C4 out pseudodihedral.dat
go
EOF

echo "#!/bin/bash
#SBATCH --mail-user=kyleghaby@uchicago.edu # Who to send emails to
##SBATCH --mail-type=ALL # Send emails on start, end and failure
#SBATCH --job-name=uUS_$i # Name to show in the job queue
#SBATCH --ntasks=1 # Total number of mpi tasks requested
#SBATCH --nodes=1
#SBATCH --time=2:00:00
#SBATCH --gres=gpu:1                     # Include GPU generic resource
#SBATCH --account=pi-roux
#SBATCH --partition=beagle3

module load amber

pmemd.cuda -O -i US_$i.mdin -o US_$i.mdout -p ../../prep/BTK_IB_u_nobadwater.parm7 -c ../../prod/US_input.rst7 -r US_$i.rst7 -x US_$i.nc -inf US_$i.mdinfo

cpptraj -i pseudodihedral.traj

./../histogram -i dihed_$i.dat -col 2  -o dihed_$i.histo -int .01

" > US_$i.slurm

RES=$(sbatch US_$i.slurm)
echo "Submitted US_$i.slurm, and the id is: ${RES##* }"
cd ..


#do the rest
for i in `seq -6 4 150`;do
cd US_$i
j=$(echo "$i-4" | bc)

cat >pseudodihedral.traj <<EOF
parm ../../prep/BTK_IB_u_nobadwater.parm7
trajin US_$i.nc
dihedral :IB@OAC :IB@CAW :IB@NBF :IB@C4 out pseudodihedral.dat
go
EOF



echo "#!/bin/bash
#SBATCH --dependency=afterok:${RES##* }
#SBATCH --mail-user=kyleghaby@uchicago.edu # Who to send emails to 
##SBATCH --mail-type=ALL # Send emails on start, end and failure 
#SBATCH --job-name=uUS_$i # Name to show in the job queue 
#SBATCH --ntasks=1 # Total number of mpi tasks requested
#SBATCH --nodes=1
#SBATCH --time=2:00:00
#SBATCH --gres=gpu:1                     # Include GPU generic resource
#SBATCH --account=pi-roux
#SBATCH --partition=beagle3

module load amber

./../get_frame.sh $j $i

pmemd.cuda -O -i US_$i.mdin -o US_$i.mdout -p ../../prep/BTK_IB_u_nobadwater.parm7 -c for_cv_$i.rst7 -r US_$i.rst7 -x US_$i.nc -inf US_$i.mdinfo

cpptraj -i pseudodihedral.traj

./../histogram -i dihed_$i.dat -col 2  -o dihed_$i.histo -int .01
 
" > US_$i.slurm

RES=$(sbatch US_$i.slurm)
echo "Submitted US_$i.slurm, and the id is: ${RES##* }"

cd ..
done
