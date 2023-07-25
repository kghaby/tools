#!/bin/bash

#parm="$1"

f="$1"

mask=':IB@OAC'
#:IB@CAD|:88@CB


cat >waters.traj <<EOF
parm /beagle3/roux/kyleghaby/kininhibs/main/BTK1_IB/md_1/linked/prep/BTK_IB_l_nobadwater.parm7
trajin BTK_IB_l_nobadwater.rst7
reference /beagle3/roux/kyleghaby/kininhibs/main/BTK1_IB/md_1/linked/prep/BTK_IB_l_nobadwater.rst7  1

watershell $mask out waters.dat !(:268-442)&(:WAT) 
go
EOF
cpptraj -i waters.traj

maskforgp=$(echo $mask | sed 's/@/\\@/g') 

./../../../US/histogram -i waters.dat -col 2  -o waters.histo -int .1

gnuplot -persist << EOF

    set term x11 1
    set multiplot layout 2,1 rowsfirst
	set grid
    #set key outside
	set key t r
    set title '$1 $maskforgp'
    set yrange [*:*]
    set ylabel 'Waters (count)'
    set xlabel 'Time (Frames)'
	plot \
        "waters.dat"   u 1:2 every 10 w l title "first",\
        "waters.dat"   u 1:3 every 10 w l title "second"


	set xlabel 'Waters (count)'
	set ylabel 'Count'
	plot \
		 "waters.histo" u 1:2 w l title "first"

pause -1 
EOF
