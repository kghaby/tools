#!/bin/bash
##!/usr/bin/python

#PULL: 25 angstroms over 400ns. 400ns split into 50ns jobs. 

##CHANGE: distance masks, harm, cv_ni, cv_i, 3 job names

######################################################
module load amber
###get min distance from prod
cat >distance_check_from_prod.traj <<EOF
parm ../../build/system.parm7
trajin ../../md/prod/prod.nc

distance @1276,2344 :267  out dist_prod.dat
EOF

cpptraj -i distance_check_from_prod.traj

initial=$(awk -v min=9999 'NR==2,NR==1000000 {if(min>$2){want=$2; min=$2}}END{print want} ' dist_prod.dat)
echo "Min from production: $initial"
###write 8 inputs
for a in {1..8}
do
##colvar files

#3.125 steps
final=$(bc<<<$initial+3.125)

cat >cv.dist.$a.in <<EOF
&colvar
        cv_type = 'COM_DISTANCE'

        npath = 2, path = $initial, $final,            ! 
        nharm = 1, harm = 5.0                   ! restraint

        cv_ni = 60                              ! 
        cv_i = 1276,2344,0,4332

 /
EOF

echo "Done making cv.dist.$a.in, which pulls from $initial to $final"

initial=$final

###smd.mdin files
cat  >smd.$a.mdin <<EOF
Input file for SMD

 &cntrl
    imin=0,        ! No minimization
    irest=1,       ! continue from prev veloc? 1-yes 0-no
    ntx=5,         ! Inpcrd file has velocities? 5-yes 1-no
    ig=-1,      ! rng seed

    ! Temperature control
    ntt=3,         ! Langevin dynamics
    gamma_ln=1.0,  ! Friction coefficient (ps^-1)
    temp0=310,   ! Target temperature

    ! Potential energy control
    cut=12.0,      ! nonbonded cutoff, in Angstroms
    fswitch=10.0,  ! Force-based switching

    ! MD settings
    nstlim=12500000, ! 400/8=50ns
    dt=0.004,      ! time step (ps)

    ! SHAKE
    ntc=2,         ! Constrain bonds containing hydrogen
    ntf=2,         ! Do not calculate forces of bonds containing hydrogen

    ! Control how often information is printed
    ntpr=1000,     ! Print energies every 1000 steps
    ntwx=5000,    ! Print coordinates every 25000 steps to the trajectory
    ntwr=5000,    ! Print a restart file every 10K steps (can be less frequent)
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
    watnam='TIP3',  ! Water residues are named WAT
    owtnm='OH2',    ! Water oxygens are named O

    ! restraints
!    ntr=1,     ! turn on restraints
!    restraint_wt=50.0,
!    restraintmask=":*",

    !Other for SMD
    infe = 1,   ! recognize smd
    jar = 1,    ! use smd restraint file
/
 &wt type='DUMPFREQ', istep1=1, /
 &wt type='END', /

 &smd
    output_file = 'smd.$a.txt'
    output_freq = 50
    cv_file = 'cv.dist.$a.in'

 &end

EOF
echo "Done making smd.$a.mdin"
done

###############################

#first sbatch file
cat >smd.1.slurm <<EOF
#!/bin/bash
#SBATCH --mail-user=kyleghaby@uchicago.edu # Who to send emails to 
#SBATCH --mail-type=ALL # Send emails on start, end and failure 
#SBATCH --job-name=smd.1
#SBATCH --time=36:00:00
#SBATCH --partition=rouxgpu
#SBATCH --qos=roux
#SBATCH --gres=gpu:1
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --constraint=gtx780
#SBATCH --nodelist=midway-l12b-02

module unload amber
module load amber 

pmemd.cuda -O -p  ../../build/system.parm7 -c ../../md/prod/prod.rst7 -i smd.1.mdin -x smd.1.nc -o smd.1.mdout -inf smd.1.mdinfo -r smd.1.rst7 -l smd.1.log -inf smd.1.mdinfo

EOF

RES=$(sbatch smd.1.slurm)
echo "Submitted smd.1.slurm, and the id is: ${RES##* }"
##################################

#other sbatch files
for a in {2..8}
do
b=$((a-1))

cat >smd.$a.slurm <<EOF
#!/bin/bash
#SBATCH --dependency=afterok:${RES##* }
#SBATCH --mail-user=kyleghaby@uchicago.edu # Who to send emails to
#SBATCH --mail-type=ALL # Send emails on start, end and failure
#SBATCH --job-name=smd.$a
#SBATCH --time=36:00:00
#SBATCH --partition=rouxgpu
#SBATCH --qos=roux
#SBATCH --gres=gpu:1
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --constraint=gtx780
#SBATCH --nodelist=midway-l12b-02

module unload amber
module load amber


pmemd.cuda -O -p  ../../build/system.parm7 -c smd.$b.rst7 -i smd.$a.mdin -x smd.$a.nc -o smd.$a.mdout -inf smd.$a.mdinfo -r smd.$a.rst7 -l smd.$a.log -inf smd.$a.mdinfo

EOF

RES=$(sbatch smd.$a.slurm)
echo "Submitted smd.$a.slurm, and the id is: ${RES##* }"
done
###################################


########################################
###make cpptraj files

##universal
cat >viewing-pdb.traj <<EOF
parm ~/scratch-midway2/projects/btk+ib/amber/chamber_heavy_H/build/system.parm7
#reference ../../md/prod/prod.rst7
trajin ../../md/prod/prod.rst7
autoimage :1-267
#strip !(:1-267<:10)
strip :TIP3,CLA,POT
trajout smd_viewing.pdb
go
EOF

cat >viewing-dcd.traj <<EOF
parm ~/scratch-midway2/projects/btk+ib/amber/chamber_heavy_H/build/system.parm7
#reference ../../md/prod/prod.rst7
trajin smd.nc
autoimage :1-267
#strip !(:1-267<:5)
strip :TIP3,CLA,POT
trajout smd_viewing.dcd
go
EOF

cat >combine_nc.traj <<EOF
parm ~/scratch-midway2/projects/btk+ib/amber/chamber_heavy_H/build/system.parm7
trajin smd.1.nc
trajin smd.2.nc
trajin smd.3.nc
trajin smd.4.nc
trajin smd.5.nc
trajin smd.6.nc
trajin smd.7.nc
trajin smd.8.nc
trajout smd.nc
EOF


echo "Done making cpptraj files for postprocessing" 

########################################
#postprocess
cat >postprocess.slurm <<EOF
#!/bin/bash
#SBATCH --dependency=afterok:${RES##* }
#SBATCH --mail-user=kyleghaby@uchicago.edu # Who to send emails to
#SBATCH --mail-type=ALL # Send emails on start, end and failure
#SBATCH --job-name=postprocess
#SBATCH --time=2:00:00
#SBATCH --partition=broadwl

module unload amber
module load amber

#make nice traj
cpptraj -i combine_nc.traj
cpptraj -i viewing-pdb.traj
cpptraj -i viewing-dcd.traj
#vmd smd_viewing*

#concat smd.N.txt and add work
./process_smd.N.txt.exe

#check system
cd check_system/potential_kinetic
./etot.exe
cd ../restraint
./restraint.exe
cd ../rmsd
cpptraj -i rmsd_check.traj
cd ../solvation
cpptraj -i solvation.traj
cd ../secstruct
cpptraj -i secstruct.traj
cd ../..

EOF

sbatch postprocess.slurm
echo "Submitted postprocess.slurm, and it will run after jobid ${RES##* }"
echo "Woo dilly"
