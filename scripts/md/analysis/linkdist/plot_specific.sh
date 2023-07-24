#!/bin/bash
set -e 

analysis_dir="linkdist"
SCRIPT=$(realpath "$0")
SCRIPT_gnu=$(echo "$SCRIPT" | sed 's/_/\\\\_/g')

#whitelist=("BTK1_IB" "BTK_4C9" "EGFR_IB" "EGFR_4C9")
whitelist=("SRC_5YZ" "AURKA_5YZ")
blacklist=()

echo "
#set term x11 size 1280,720

set term png size 1920,1080
set output 'plot.png'
set key font \",32\"
set xtics font \",32\"

#set multiplot layout 4,5 rowsfirst
#set lmargin 1
#set rmargin 1
#set tmargin 1
#set bmargin 1.2
#set label 1 \"$SCRIPT_gnu\" at screen 0.5, screen 0.99 center
#set label 2 \"Distance (A)\" at screen 0.5, screen 0.01 center
#set label 3 \"Count\" at screen 0.01, screen 0.5 center rotate by 90
set key t r
unset ytics
#set logscale y
set xrange [0:20]
plot\\" > plot.gnu
for dir in /beagle3/roux/kyleghaby/kininhibs/main/*/md/13; do

#get name of system
IFS='/' read -ra arrDir <<< $dir
system=$(echo "${arrDir[6]}")

#check whitelist
if (("${#whitelist[@]}" > 0 )); then
if [[ ! " ${whitelist[*]} " =~ " ${system} " ]]; then
echo "$system IS NOT WHITELISTED...............SKIPPING"
continue
fi
fi

#check blacklist
if (( "${#blacklist[@]}" > 0 )); then
if [[ " ${blacklist[*]} " =~ " ${system} " ]]; then
echo "$system IS BLACKLISTED...............SKIPPING"
continue
fi
fi

#get name of system
IFS='/' read -ra arrDir <<< $dir
system=$(echo "${arrDir[6]}" | sed 's/_/-/g')

#get xtal val
xtalval=$(tail -1 "$dir/unlinked/prod/analysis/${analysis_dir}/xtal.dat" | awk '{print $2}')

#add system to gnuplot file
echo "#plot\\
#\"$dir/linked/prod/analysis/${analysis_dir}/data.histo\" u 1:2 every 1 w l lw 1 lc rgb \"slateblue1\" title \"L\",\\
#plot\\
\"$dir/unlinked/prod/analysis/${analysis_dir}/data.histo\" u 1:2 every 1 w l lw 3  title \"           \",\\
" >> plot.gnu
done

#hold plot
echo "
#pause -1" >> plot.gnu


echo "delete commented lines between plot command and plot functions in plot.gnu"
gnuplot plot.gnu

