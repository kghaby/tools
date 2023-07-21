#!/bin/bash
set -e 



echo 'set ylabel "Frequency"
set xlabel "Colvar"
plot\\
' > plot_histo.gnu
for i in 10 42
do 
for j in `seq 1 1 10`
do 
echo "\"../US_$i/dihed_$i.$j.histo\" u 1:2 every 10 w l notitle,\\" >> plot_histo.gnu  
done
done  
for j in `seq 1 1 9`
do
echo "\"../US_102/dihed_102.$j.histo\" u 1:2 every 10 w l notitle,\\" >> plot_histo.gnu
done
echo "\"../US_102/dihed_102.10.histo\" u 1:2 every 10 w l notitle
pause -1" >> plot_histo.gnu   


gnuplot plot_histo.gnu
