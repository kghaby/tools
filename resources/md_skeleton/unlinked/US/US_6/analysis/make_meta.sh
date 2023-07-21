#!/bin/bash

rm meta.dat

k="0.00158392" #units: kcal/mol/deg^2. converted from  kcal/mol/rad^2. note that amber uses k(x)^2 while wham uses 0.5k(x)^2, so to convert multiply the amber force constant by 2(pi/180)^2 = 0.0006092 

for i in 10 42 102
do 
echo "../US_$i/dihed_$i.1.dat    $i.0    $k" >> meta.dat
echo "../US_$i/dihed_$i.2.dat    $i.0    $k" >> meta.dat
echo "../US_$i/dihed_$i.3.dat    $i.0    $k" >> meta.dat
echo "../US_$i/dihed_$i.4.dat    $i.0    $k" >> meta.dat
echo "../US_$i/dihed_$i.5.dat    $i.0    $k" >> meta.dat
echo "../US_$i/dihed_$i.6.dat    $i.0    $k" >> meta.dat
echo "../US_$i/dihed_$i.7.dat    $i.0    $k" >> meta.dat
echo "../US_$i/dihed_$i.8.dat    $i.0    $k" >> meta.dat
echo "../US_$i/dihed_$i.9.dat    $i.0    $k" >> meta.dat
echo "../US_$i/dihed_$i.10.dat   $i.0    $k" >> meta.dat
done  
