#!/bin/bash
set -e 



echo 'set ylabel "Frequency"
set xlabel "Colvar"
plot\\
' > plot_histo.gnu
for i in `seq -10 4 146`;do 
echo "\"../US_$i/dihed_$i.histo\" u 1:2 w l notitle,\\" >> plot_histo.gnu  
done  
echo "\"../US_150/dihed_150.histo\" u 1:2 w l notitle
pause -1" >> plot_histo.gnu   


gnuplot plot_histo.gnu
