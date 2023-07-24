#!/bin/bash

#need to change k_amber, seq's, and grad input denom

k_amber=200
k_wham=$(echo "$k_amber*0.0006092" | bc)   #units: kcal/mol/deg^2. converted from  kcal/mol/rad^2. note that amber uses k(x)^2 while wham uses 0.5k(x)^2, so to convert multiply the amber force constant by 2(pi/180)^2 = 0.0006092

seq_upper=20

rm -Ir series
mkdir -p series
cd series 

for j in `seq 1 1 $seq_upper`
do
	for i in `seq -10 4 150`
	do
		echo "../../US_$i/dihed_$i.$j.dat   $i.0    $k_wham" >> meta.$j.dat
	done
~/utilities/wham/wham/wham/wham P -11 151 41 0.01 310 0 meta.$j.dat pmf.$j.dat
done



echo "set ylabel \"Energy (kcal/mol)\"
set xlabel \"Pseudodihedral (deg)\"
set title \"PMFs for 10 ns chunks\"
set key outside

set palette defined (0 'light-salmon', 1 'midnight-blue')
set style data lines
unset colorbox

plot\\" > plot_pmf_series.gnu
for j in `seq 1 1 $seq_upper`
do
	echo "\"pmf.$j.dat\" u 1:2 every 1 lw 1 lt palette frac ((${j}.0)/(${seq_upper}.0)) title \"$j\",\\" >> plot_pmf_series.gnu
done
echo "  
pause -1" >> plot_pmf_series.gnu


gnuplot plot_pmf_series.gnu

cd ..
