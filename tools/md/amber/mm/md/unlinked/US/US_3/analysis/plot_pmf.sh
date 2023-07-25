#!/bin/bash


gnuplot -persist << EOF
    set key b r
    set title 'WHAM output'
    set yrange [*:*]
    set ylabel 'Energy (kcal/mol)'
    set xlabel 'Pseudodihedral (deg)'
    plot \
"pmf.dat"   u 1:2 every 1 w l title ""
    pause -1


EOF

