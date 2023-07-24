
set term x11 size 1280,720
set multiplot layout 4,4 rowsfirst
set lmargin 1
set rmargin 1
set tmargin 1
set bmargin 1.2
#set label 1 "/beagle3/roux/kyleghaby/kininhibs/main/analysis/dist\\_com/plot.sh" at screen 0.5, screen 0.99 center
set label 2 "Distance (A)" at screen 0.5, screen 0.01 center
#set label 3 "Count" at screen 0.01, screen 0.5 center rotate by 90
set key t r
unset ytics
#set logscale y



set label 9 "BTK1-IB" at graph 0.5, graph 0.90 center
set arrow 10 from 8.2996,graph 0 to 8.2996,graph 1 nohead lw 2 lc rgb "#000000" front
set label 10 "X" at 8.2996, graph -0.05 center
set xrange [0:*]

plot\
"/beagle3/roux/kyleghaby/kininhibs/main/BTK1_IB/md/13/linked/prod/analysis/dist_com/data.histo" u 1:2 every 1 w l lw 1 lc rgb "slateblue1" title "L",\
"/beagle3/roux/kyleghaby/kininhibs/main/BTK1_IB/md/13/unlinked/prod/analysis/dist_com/data.histo" u 1:2 every 1 w l lw 1 lc rgb "dark-orange" title "U"


set label 9 "EGFR-AB" at graph 0.5, graph 0.90 center
set arrow 10 from 6.8351,graph 0 to 6.8351,graph 1 nohead lw 2 lc rgb "#000000" front
set label 10 "X" at 6.8351, graph -0.05 center
set xrange [0:*]

plot\
"/beagle3/roux/kyleghaby/kininhibs/main/EGFR_AB/md/13/linked/prod/analysis/dist_com/data.histo" u 1:2 every 1 w l lw 1 lc rgb "slateblue1" title "L",\
"/beagle3/roux/kyleghaby/kininhibs/main/EGFR_AB/md/13/unlinked/prod/analysis/dist_com/data.histo" u 1:2 every 1 w l lw 1 lc rgb "dark-orange" title "U"


set label 9 "EGFR-DB" at graph 0.5, graph 0.90 center
set arrow 10 from 5.9787,graph 0 to 5.9787,graph 1 nohead lw 2 lc rgb "#000000" front
set label 10 "X" at 5.9787, graph -0.05 center
set xrange [0:*]

plot\
"/beagle3/roux/kyleghaby/kininhibs/main/EGFR_DB/md/13/linked/prod/analysis/dist_com/data.histo" u 1:2 every 1 w l lw 1 lc rgb "slateblue1" title "L",\
"/beagle3/roux/kyleghaby/kininhibs/main/EGFR_DB/md/13/unlinked/prod/analysis/dist_com/data.histo" u 1:2 every 1 w l lw 1 lc rgb "dark-orange" title "U"


set label 9 "EGFR-IB" at graph 0.5, graph 0.90 center
set arrow 10 from 7.6735,graph 0 to 7.6735,graph 1 nohead lw 2 lc rgb "#000000" front
set label 10 "X" at 7.6735, graph -0.05 center
set xrange [0:*]

plot\
"/beagle3/roux/kyleghaby/kininhibs/main/EGFR_IB/md/13/linked/prod/analysis/dist_com/data.histo" u 1:2 every 1 w l lw 1 lc rgb "slateblue1" title "L",\
"/beagle3/roux/kyleghaby/kininhibs/main/EGFR_IB/md/13/unlinked/prod/analysis/dist_com/data.histo" u 1:2 every 1 w l lw 1 lc rgb "dark-orange" title "U"


set label 9 "EGFR-O44" at graph 0.5, graph 0.90 center
set arrow 10 from 7.5981,graph 0 to 7.5981,graph 1 nohead lw 2 lc rgb "#000000" front
set label 10 "X" at 7.5981, graph -0.05 center
set xrange [0:*]

plot\
"/beagle3/roux/kyleghaby/kininhibs/main/EGFR_O44/md/13/linked/prod/analysis/dist_com/data.histo" u 1:2 every 1 w l lw 1 lc rgb "slateblue1" title "L",\
"/beagle3/roux/kyleghaby/kininhibs/main/EGFR_O44/md/13/unlinked/prod/analysis/dist_com/data.histo" u 1:2 every 1 w l lw 1 lc rgb "dark-orange" title "U"


set label 9 "EGFR-OB" at graph 0.5, graph 0.90 center
set arrow 10 from 5.6808,graph 0 to 5.6808,graph 1 nohead lw 2 lc rgb "#000000" front
set label 10 "X" at 5.6808, graph -0.05 center
set xrange [0:*]

plot\
"/beagle3/roux/kyleghaby/kininhibs/main/EGFR_OB/md/13/linked/prod/analysis/dist_com/data.histo" u 1:2 every 1 w l lw 1 lc rgb "slateblue1" title "L",\
"/beagle3/roux/kyleghaby/kininhibs/main/EGFR_OB/md/13/unlinked/prod/analysis/dist_com/data.histo" u 1:2 every 1 w l lw 1 lc rgb "dark-orange" title "U"


set label 9 "EPHB3-6P6" at graph 0.5, graph 0.90 center
set arrow 10 from 7.3454,graph 0 to 7.3454,graph 1 nohead lw 2 lc rgb "#000000" front
set label 10 "X" at 7.3454, graph -0.05 center
set xrange [0:*]

plot\
"/beagle3/roux/kyleghaby/kininhibs/main/EPHB3_6P6/md/13/linked/prod/analysis/dist_com/data.histo" u 1:2 every 1 w l lw 1 lc rgb "slateblue1" title "L",\
"/beagle3/roux/kyleghaby/kininhibs/main/EPHB3_6P6/md/13/unlinked/prod/analysis/dist_com/data.histo" u 1:2 every 1 w l lw 1 lc rgb "dark-orange" title "U"


set label 9 "JAK3-PF" at graph 0.5, graph 0.90 center
set arrow 10 from 6.3766,graph 0 to 6.3766,graph 1 nohead lw 2 lc rgb "#000000" front
set label 10 "X" at 6.3766, graph -0.05 center
set xrange [0:*]

plot\
"/beagle3/roux/kyleghaby/kininhibs/main/JAK3_PF/md/13/linked/prod/analysis/dist_com/data.histo" u 1:2 every 1 w l lw 1 lc rgb "slateblue1" title "L",\
"/beagle3/roux/kyleghaby/kininhibs/main/JAK3_PF/md/13/unlinked/prod/analysis/dist_com/data.histo" u 1:2 every 1 w l lw 1 lc rgb "dark-orange" title "U"


set label 9 "MKK7-IB" at graph 0.5, graph 0.90 center
set arrow 10 from 9.1964,graph 0 to 9.1964,graph 1 nohead lw 2 lc rgb "#000000" front
set label 10 "X" at 9.1964, graph -0.05 center
set xrange [0:*]

plot\
"/beagle3/roux/kyleghaby/kininhibs/main/MKK7_IB/md/13/linked/prod/analysis/dist_com/data.histo" u 1:2 every 1 w l lw 1 lc rgb "slateblue1" title "L",\
"/beagle3/roux/kyleghaby/kininhibs/main/MKK7_IB/md/13/unlinked/prod/analysis/dist_com/data.histo" u 1:2 every 1 w l lw 1 lc rgb "dark-orange" title "U"


set label 9 "SRC-DGY" at graph 0.5, graph 0.90 center
set arrow 10 from 7.0503,graph 0 to 7.0503,graph 1 nohead lw 2 lc rgb "#000000" front
set label 10 "X" at 7.0503, graph -0.05 center
set xrange [0:*]

plot\
"/beagle3/roux/kyleghaby/kininhibs/main/SRC_DGY/md/13/linked/prod/analysis/dist_com/data.histo" u 1:2 every 1 w l lw 1 lc rgb "slateblue1" title "L",\
"/beagle3/roux/kyleghaby/kininhibs/main/SRC_DGY/md/13/unlinked/prod/analysis/dist_com/data.histo" u 1:2 every 1 w l lw 1 lc rgb "dark-orange" title "U"


set label 9 "SRC-O44" at graph 0.5, graph 0.90 center
set arrow 10 from 8.0758,graph 0 to 8.0758,graph 1 nohead lw 2 lc rgb "#000000" front
set label 10 "X" at 8.0758, graph -0.05 center
set xrange [0:*]

plot\
"/beagle3/roux/kyleghaby/kininhibs/main/SRC_O44/md/13/linked/prod/analysis/dist_com/data.histo" u 1:2 every 1 w l lw 1 lc rgb "slateblue1" title "L",\
"/beagle3/roux/kyleghaby/kininhibs/main/SRC_O44/md/13/unlinked/prod/analysis/dist_com/data.histo" u 1:2 every 1 w l lw 1 lc rgb "dark-orange" title "U"


set label 9 "SRC-PD" at graph 0.5, graph 0.90 center
set arrow 10 from 8.4012,graph 0 to 8.4012,graph 1 nohead lw 2 lc rgb "#000000" front
set label 10 "X" at 8.4012, graph -0.05 center
set xrange [0:*]

plot\
"/beagle3/roux/kyleghaby/kininhibs/main/SRC_PD/md/13/linked/prod/analysis/dist_com/data.histo" u 1:2 every 1 w l lw 1 lc rgb "slateblue1" title "L",\
"/beagle3/roux/kyleghaby/kininhibs/main/SRC_PD/md/13/unlinked/prod/analysis/dist_com/data.histo" u 1:2 every 1 w l lw 1 lc rgb "dark-orange" title "U"


set label 9 "TAK1-OL" at graph 0.5, graph 0.90 center
set arrow 10 from 4.5964,graph 0 to 4.5964,graph 1 nohead lw 2 lc rgb "#000000" front
set label 10 "X" at 4.5964, graph -0.05 center
set xrange [0:*]

plot\
"/beagle3/roux/kyleghaby/kininhibs/main/TAK1_OL/md/13/linked/prod/analysis/dist_com/data.histo" u 1:2 every 1 w l lw 1 lc rgb "slateblue1" title "L",\
"/beagle3/roux/kyleghaby/kininhibs/main/TAK1_OL/md/13/unlinked/prod/analysis/dist_com/data.histo" u 1:2 every 1 w l lw 1 lc rgb "dark-orange" title "U"


pause -1
