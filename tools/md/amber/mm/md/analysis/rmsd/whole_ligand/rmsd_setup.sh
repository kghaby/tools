#!/bin/bash 
set -ea

KIN_LIG="EGFR_IB"
refpdbf="../../../linked/prep/${KIN_LIG}_l.pdb"

l_parm="../../../linked/prep/${KIN_LIG}_l.parm7"
u_parm="../../../unlinked/prep/${KIN_LIG}_u.parm7"

l_traj=() #keep empty
b=0
for a in {1..10}; do
    l_traj[$b]="../../../linked/prod/prod.${a}.nc"
    b=$b+1  
done

u_traj=() #keep empty
b=0
for a in {1..10}; do
    u_traj[$b]="../../../unlinked/prod/prod.${a}.nc"
    b=$b+1
done

protmask='(@CA)' #,C,O,N)'
xtalprotmask=$protmask
ligmask=':IB@CAA,CAD,CAW,OAC,NBG,CAO,CAP,CAQ,CAR,CBE,NBF,NAU,CBB,N1,C2,N3,C4,C5,C6,NAB,CBA,CAK,CAL,CAM,CAN,CAZ,OAV,CAY,CAE,CAF,CAG,CAI,CAJ'
xtalligmask=$ligmask


echo "setting up rmsd's for $ligmask"

###########
# make cpptraj files
###########

# ref xtal

## linked
echo "making rmsd_l_refx.traj" 
cat >rmsd_l_refx.traj <<EOF
parm $l_parm [linked]
parm $l_parm [xtal]
EOF
for f in ${l_traj[@]}; do
cat >>rmsd_l_refx.traj <<EOF 
trajin $f parm [linked]
EOF
done
cat >>rmsd_l_refx.traj <<EOF
autoimage
reference $refpdbf parm [xtal] [xtalcoords]
rmsd rmsd_l_refx_prot $protmask $xtalprotmask out rmsd_l_refx_prot.dat ref [xtalcoords] mass 
rmsd rms_l_refx_lig $ligmask $xtalligmask nofit out rmsd_l_refx_lig.dat ref [xtalcoords] mass
go
EOF



## unlinked
echo "making rmsd_l_refx.traj" 
cat >rmsd_u_refx.traj <<EOF
parm $u_parm [unlinked]
parm $l_parm [xtal]
EOF
for f in ${u_traj[@]}; do
cat >>rmsd_u_refx.traj <<EOF
trajin $f parm [unlinked]
EOF
done
cat >>rmsd_u_refx.traj <<EOF
autoimage
reference $refpdbf parm [xtal] [xtalcoords]
rmsd rmsd_u_refx_prot $protmask $xtalprotmask out rmsd_u_refx_prot.dat ref [xtalcoords] mass
rmsd rmsd_u_refx_lig $ligmask $xtalligmask nofit out rmsd_u_refx_lig.dat ref [xtalcoords] mass
go
EOF

# ref linked

## linked
echo "making rmsd_l_refl.traj" 
cat >rmsd_l_refl.traj <<EOF
parm $l_parm [linked]
parm $refpdbf [xtal]
EOF
for f in ${l_traj[@]}; do
cat >>rmsd_l_refl.traj <<EOF
trajin $f parm [linked]
EOF
done
cat >>rmsd_l_refl.traj <<EOF
autoimage
reference $refpdbf parm [xtal] [xtalcoords]
reference ${l_traj[0]} 1 parm [linked] [linkedcoords]
crdaction [linkedcoords] rmsd l_xtal_align $protmask $xtalprotmask ref [xtalcoords] mass
rmsd rmsd_l_refl_prot $protmask $xtalprotmask out rmsd_l_refl_prot.dat ref [xtalcoords] mass
rmsd rmsd_l_refl_lig $ligmask $ligmask nofit out rmsd_l_refl_lig.dat ref [linkedcoords] mass
go
EOF


## unlinked
echo "making rmsd_u_refl.traj"  
cat >rmsd_u_refl.traj <<EOF
parm $u_parm [unlinked]
parm $l_parm [linked]
parm $refpdbf [xtal]
EOF
for f in ${u_traj[@]}; do
cat >>rmsd_u_refl.traj <<EOF
trajin $f parm [unlinked]
EOF
done
cat >>rmsd_u_refl.traj <<EOF
autoimage
reference $refpdbf parm [xtal] [xtalcoords]
reference ${l_traj[0]} 1 parm [linked] [linkedcoords]
crdaction [linkedcoords] rmsd l_xtal_align $protmask $xtalprotmask ref [xtalcoords] mass
rmsd rmsd_u_refl_prot $protmask $xtalprotmask out rmsd_u_refl_prot.dat ref [xtalcoords] mass
rmsd rmsd_u_refl_lig $ligmask $ligmask nofit out rmsd_u_refl_lig.dat ref [linkedcoords] mass
go
EOF


