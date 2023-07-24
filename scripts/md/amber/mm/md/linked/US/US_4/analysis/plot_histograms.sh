#!/bin/bash
set -e 



echo 'set ylabel "Frequency"
set xlabel "Pseudodihedral (deg)"
plot\\
' > plot_histo.gnu
for i in 10 46
do 
for j in `seq 3 1 18`
do 
echo "\"../US_$i/dihed_$i.$j.histo\" u 1:2 every 10 w l notitle,\\" >> plot_histo.gnu  
done
done  
for j in `seq 3 1 17`
do
echo "\"../US_106/dihed_106.$j.histo\" u 1:2 every 10 w l notitle,\\" >> plot_histo.gnu
done
echo "\"../US_106/dihed_106.18.histo\" u 1:2 every 10 w l notitle
pause -1" >> plot_histo.gnu   


gnuplot plot_histo.gnu
