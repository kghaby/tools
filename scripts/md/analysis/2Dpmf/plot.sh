#!/bin/bash
set -e 

analysis_dirx="linkdist"
analysis_diry="rmsd_from_xtal"
SCRIPT=$(realpath "$0")
SCRIPT_gnu=$(echo "$SCRIPT" | sed 's/_/\\\\_/g')

echo "
set term x11 size 1280,720
set multiplot layout 4,4 rowsfirst
set lmargin 1
set rmargin 1
set tmargin 1
set bmargin 1.2
#set label 1 \"$SCRIPT_gnu\" at screen 0.5, screen 0.99 center
#set label 2 \"Distance (A)\" at screen 0.5, screen 0.01 center
#set label 3 \"Count\" at screen 0.01, screen 0.5 center rotate by 90
set pm3d map
set key t r
unset ytics
#set logscale y

" > plot.gnu
for dir in /beagle3/roux/kyleghaby/kininhibs/main/*/md/13; do

#get name of system
IFS='/' read -ra arrDir <<< $dir
system=$(echo "${arrDir[6]}" | sed 's/_/-/g')

#get xtal val
xtalvalx=$(tail -1 "$dir/linked/prod/analysis/${analysis_dirx}/xtal.dat" | awk '{print $2}')
xtalvaly=$(tail -1 "$dir/linked/prod/analysis/${analysis_diry}/xtal.dat" | awk '{print $2}')

#add system to gnuplot file
echo "
set label 9 \"$system\" at graph 0.5, graph 0.90 center
set label 10 \"X\" at $xtalvalx, $xtalvaly center
#set xrange [0:*]
#set yrange [0:*]

#plot\\
#\"$dir/linked/prod/analysis/${analysis_dir}/data.histo\" u 1:2 every 1 w l lw 1 lc rgb \"slateblue1\" title \"L\",\\

plot\\
\"$dir/unlinked/prod/analysis/${analysis_dir}/data.histo\" u 1:2 every 1 w l lw 1 lc rgb \"dark-orange\" title \"U\"
" >> plot.gnu
done

#hold plot
echo "
pause -1" >> plot.gnu


gnuplot plot.gnu
