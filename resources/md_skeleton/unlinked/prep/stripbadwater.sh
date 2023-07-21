#!/bin/bash

#removes none of the xtal waters

parm7="../../../build/BTK_IB_u.parm7"
rst7="../../../build/BTK_IB_u.rst7"
system="BTK_IB_u"
ligand="IB"
xtal_wat_resIDs="268-442"
cutoff="5" #second water shell

cat >stripbadwater_parm7.traj <<EOF
parm $parm7
reference $rst7 1

parmstrip (:$ligand<:$cutoff)&:WAT&!(:$xtal_wat_resIDs)

parmwrite out ${system}_nobadwater.parm7
go
EOF

cat >stripbadwater_rst7.traj <<EOF
parm $parm7
trajin $rst7
reference $rst7 1

strip (:$ligand<:$cutoff)&:WAT&!(:$xtal_wat_resIDs)

trajout ${system}_nobadwater.rst7
go
EOF

cpptraj -i stripbadwater_parm7.traj
cpptraj -i stripbadwater_rst7.traj




