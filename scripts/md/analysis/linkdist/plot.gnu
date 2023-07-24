
#set term x11 size 1280,720

set term png size 1920,1080
set output 'plot.png'
set key font ",32"
set xtics font ",32"

#set multiplot layout 4,5 rowsfirst
#set lmargin 1
#set rmargin 1
#set tmargin 1
#set bmargin 1.2
#set label 1 "/beagle3/roux/kyleghaby/kininhibs/main/analysis/linkdist/plot\\_specific.sh" at screen 0.5, screen 0.99 center
#set label 2 "Distance (A)" at screen 0.5, screen 0.01 center
#set label 3 "Count" at screen 0.01, screen 0.5 center rotate by 90
set key t r
unset ytics
#set logscale y
set xrange [0:20]
plot\
"/beagle3/roux/kyleghaby/kininhibs/main/AURKA_5YZ/md/13/unlinked/prod/analysis/linkdist/data.histo" u 1:2 every 1 w l lw 3  title "           ",\
"/beagle3/roux/kyleghaby/kininhibs/main/SRC_5YZ/md/13/unlinked/prod/analysis/linkdist/data.histo" u 1:2 every 1 w l lw 3  title "           ",\


#pause -1
