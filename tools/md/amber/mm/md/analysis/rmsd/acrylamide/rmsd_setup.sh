#!/bin/bash 
set -ea

#files
refpdbf="../../xtal/5P9J_reres_noaltloc.pdb"

l_parm="../../../linked/amber/step3_charmm2amber_hmr.parm7"
u_parm="../../../unlinked/amber/step3_charmm2amber_hmr.parm7"

l_traj=() #keep empty
b=0
for a in {4..21}; do
    l_traj[$b]="../../../linked/amber/step5_${a}_hmr.nc"
    b=$b+1  
done

u_traj=() #keep empty
b=0
for a in {4..21}; do
    u_traj[$b]="../../../unlinked/amber/step5_${a}_hmr.nc"
    b=$b+1
done

#masks
protmask='(:2-87,89-159,163-265)&(@CA)' #,C,O,N)'
xtalprotmask='(:2-87,89-262)&(@CA,C,O,N)'
ligmask=':IB@CAA,CAD,CAW,OAC,NBG,CAO,CAP,CAQ,CAR,CBE'
xtalligmask=':8E8@CAA,CAD,CAW,OAC,NBG,CAO,CAP,CAQ,CAR,CBE'


echo "setting up rmsd's for $ligmask"

###########
# make cpptraj files
###########

# ref xtal

## linked
echo "making rmsd_l_refx.traj" 
cat >rmsd_l_refx.traj <<EOF
parm $l_parm [linked]
parm $refpdbf [xtal]
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
parm $refpdbf [xtal]
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


