#!/bin/bash

rm meta.dat

k="0.12184" #units: kcal/mol/deg^2. converted from 200 kcal/mol/rad^2

for i in `seq -10 4 150`;do 
echo "../US_$i/dihed_$i.dat 	$i.0 	$k" >> meta.dat
done  
