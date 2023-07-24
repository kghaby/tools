
set term png size 1080,1080
set output 'plot.png'
set key font ",24"
set xtics font ",20"
#set multiplot layout 4,4 rowsfirst
#set lmargin 1
#set rmargin 1
#set tmargin 1
#set bmargin 1.2
#set label 1 "/beagle3/roux/kyleghaby/kininhibs/main/analysis/rmsd\\_from\\_xtal/plot.sh" at screen 0.5, screen 0.99 center
set xlabel "RMSD (A)" 
#set label 3 "Count" at screen 0.01, screen 0.5 center rotate by 90
set key t r
unset ytics
#set logscale y



#set label 9 "EGFR-IB" at graph 0.5, graph 0.90 center
#set arrow 10 from 0.0000,graph 0 to 0.0000,graph 1 nohead lw 2 lc rgb "#000000" front
#set label 10 "X" at 0.0000, graph -0.05 center
set xrange [0:*]

plot\
"/beagle3/roux/kyleghaby/kininhibs/main/SRC_DGY/md/13/linked/prod/analysis/rmsd_from_xtal/data.histo" u 1:2 every 1 w l lw 3 lc rgb "slateblue1" title "L",\
"/beagle3/roux/kyleghaby/kininhibs/main/SRC_DGY/md/13/unlinked/prod/analysis/rmsd_from_xtal/data.histo" u 1:2 every 1 w l lw 3 lc rgb "dark-orange" title "U"


#pause -1
