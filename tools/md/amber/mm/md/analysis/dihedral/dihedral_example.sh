#!/bin/bash

KIN_LIG="EGFR_IB"
mask=':IB@CAP :IB@CBE :IB@NBF :IB@NAU'   
first_iter=1
last_iter=10

maincommand="dihedral $mask out dihedral.dat "


parm_l="../../linked/prep/${KIN_LIG}_l.parm7"
parm_u="../../unlinked/prep/${KIN_LIG}_u.parm7"

#xtal 
cat >xtal.traj <<EOF
parm $parm_l
trajin ../../linked/prep/${KIN_LIG}_l.pdb
autoimage
$maincommand
EOF
cpptraj -i xtal.traj
xtalval=$(tail -1 dihedral.dat | awk '{print $2}')

#linked
set -e; cd ../../linked/prod; set +e

cat >dihedral.traj <<EOF
parm $parm_l
EOF
for i in `seq $first_iter 1 $last_iter`
do
cat >>dihedral.traj <<EOF
trajin prod.$i.nc
EOF
done
cat >>dihedral.traj <<EOF
autoimage
$maincommand
go
EOF

cpptraj -i dihedral.traj
../../../../../code/histogram -i dihedral.dat -col 2  -o dihedral.histo -int 1

cd -

#unlinked
set -e; cd ../../unlinked/prod; set +e

cat >dihedral.traj <<EOF
parm $parm_u
EOF
for i in `seq $first_iter 1 $last_iter`
do
cat >>dihedral.traj <<EOF
trajin prod.$i.nc
EOF
done
cat >>dihedral.traj <<EOF
autoimage
$maincommand
go
EOF

cpptraj -i dihedral.traj
../../../../../code/histogram -i dihedral.dat -col 2  -o dihedral.histo -int 1

cd -

#plot
dir=$(pwd)
dir_gnu=$(echo "$dir" | sed 's/_/\\_/g')
mask_gnu=$(echo "$mask" | sed 's/@//g' | sed 's/://g' | sed 's/ /-/g')

fl1[0]="../../linked/prod/dihedral.dat"
fl1[1]="../../unlinked/prod/dihedral.dat"
fl2[0]="../../linked/prod/dihedral.histo"
fl2[1]="../../unlinked/prod/dihedral.histo"

findmax () {
    local array
    array=("$@")
    local ymax=0
    for f in ${array[@]}; do
        y=`awk -v N=2 'BEGIN{a=   0}{if ($N>0+a) a=$N} END{print a}' $f`
        if (( $(echo "$y > $ymax" | bc -l) )) ; then
            ymax=$y
        fi
    done
    ymax=$(echo "$y + 0.5" | bc -l)
    echo "$ymax"
}


ymax1=$(findmax ${fl1[@]})
yticmax1=$(echo "$ymax1" | awk '{print int($1-0.5)}')

ymax2=$(findmax ${fl2[@]})
yticmax2=$(echo "$ymax2" | awk '{print int($1-0.5)}')


gnuplot -persist << EOF

    #set term postscript eps enhanced color size 12,6 background rgb 'white' font ",12"
    #set output "rmsd.eps"

#    set term png enhanced size 1440,2160 font "Arial,24"
#	set output "dihedral.png"

    set encoding iso_8859_1


    set multiplot layout 2,1 rowsfirst

    set grid
    set key b r
    set title "$dir_gnu prod $mask_gnu"

#    set yrange [*:$ymax1]
#    set ytics 0, 1, $yticmax1
    #set ytics offset 0,0.5
    set ylabel 'Dihedral (deg)'
    set xlabel 'Time (ns)'
	set arrow 1 from graph 0,first $xtalval to graph 1, first $xtalval nohead lw 2 lc rgb "#000000" front
    set label 1 "X" at graph -0.002, first $xtalval right
	plot \
    "${fl1[0]}"   u (0.04 * column(1)):2 every 10 w l lw 1 lc rgb "slateblue1" title "L",\
    "${fl1[1]}"   u (0.04 * column(1)):2 every 10 w l lw 1 lc rgb "dark-orange" title "U"

 #   set yrange [*:$ymax2]
 #   set ytics 0, 1, $yticmax2
    set notitle
    set key off
    #set ytics offset 0,-0.5
    set ylabel 'Count'
    set xlabel 'Dihedral (deg)'
    set arrow 1 from $xtalval,graph 0 to $xtalval,graph 1 nohead lw 2 lc rgb "#000000" front
    set label 1 "X" at $xtalval, graph -0.03 center
    plot \
    "${fl2[0]}"   u (1 * column(1)):2 every 1 w l lw 1 lc rgb "slateblue1" title "L",\
    "${fl2[1]}"   u (1 * column(1)):2 every 1 w l lw 1 lc rgb "dark-orange" title "U"
    pause -1


EOF

#eog dihedral.png 


