#!/bin/bash

prev=$1
current=$2

frame=$(awk -v c=2 -v t=$current 'NR==1{d=$c-t;d=d<0?-d:d;v=$1;next}{m=$c-t;m=m<0?-m:m}m<d{d=m;v=$1}END {print v} ' ../US_$prev/pseudodihedral.dat)                                                                        
cpptrajinput="for_cv_"$current".traj"
cat >$cpptrajinput <<EOF
parm ../../prep/BTK_IB_l_nobadwater.parm7
trajin ../US_$prev/US_$prev.nc $frame $frame 1
trajout for_cv_$current.rst7 restart
EOF

cpptraj -i $cpptrajinput

echo "took frame $frame from ../US_$prev/US_$prev.nc, which should be when the cv is near $current" 
