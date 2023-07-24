#!/bin/bash
set -e

fl1[0]="rmsd_l_refx_lig.histo" #l
fl1[1]="rmsd_u_refx_lig.histo" #u
fl2[0]="rmsd_l_refl_lig.histo" #l
fl2[1]="rmsd_u_refl_lig.histo" #u

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
    #ymax=$(echo "$y * 1.1" | bc -l)
    echo "$ymax"
}


ymax1=$(findmax ${fl1[@]})
yticmax1=$(echo "$ymax1 * 0.9" | bc -l)
yticmax1=$(awk -v n=$yticmax1 'BEGIN{print int((n+5)/10) * 10}')

ymax2=$(findmax ${fl2[@]})
yticmax2=$(echo "$ymax2 * 0.9" | bc -l)
yticmax2=$(awk -v n=$yticmax2 'BEGIN{print int((n+5)/10) * 10}')

gnuplot -persist << EOF

    #set term postscript eps enhanced color size 12,6 background rgb 'white' font ",12"
    #set output "rmsd.eps"

#    set term wxt 0 enhanced size 1280,720 font "Arial,12"

    set encoding iso_8859_1


    set multiplot layout 2,1 rowsfirst
    TMARGIN = "set tmargin at screen 0.90; set bmargin at screen 0.50"
    BMARGIN = "set tmargin at screen 0.50; set bmargin at screen 0.10"
    SIDEMARGIN = "set lmargin at screen 0.15; set rmargin at screen 0.95"

    set grid
    set key t r
    set key spacing 1
    set title 'Histograms of IB RMSDs'
    set xrange [0:*]

#    set yrange [0:$ymax1]
#    set ytics 0, ($yticmax1 * 0.1), $yticmax1
    #set ytics offset 0,0.5
    set ylabel 'Count (from xtal state)'
    set format x ""
    @TMARGIN; @SIDEMARGIN
    plot \
    "${fl1[0]}"   u (0.1 * column(1)):2 every 10 w l lc rgb "slateblue1" title "L",\
    "${fl1[1]}"   u (0.1 * column(1)):2 every 10 w l lc rgb "dark-orange" title "U"

    set yrange [0:$ymax2]
    set ytics 0, ($yticmax2 * 0.1), $yticmax2
    set notitle
    set key off
    #set ytics offset 0,-0.5
    set xlabel 'RMSD ({\305})'
    set ylabel 'Count (from linked state)'
    set format x
    @BMARGIN; @SIDEMARGIN
    plot \
    "${fl2[0]}"   u (1 * column(1)):2 every 10 w l lc rgb "slateblue1" title "L",\
    "${fl2[1]}"   u (1 * column(1)):2 every 10 w l lc rgb "dark-orange" title "U"
    pause -1


EOF


