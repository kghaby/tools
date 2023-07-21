#!/bin/bash


rm -r restarts
mkdir restarts
cd restarts

for i in `seq 16.5 1 36.5`;do
awk -v c=2 -v t=$i 'NR==1{d=$c-t;d=d<0?-d:d;v=$1;next}{m=$c-t;m=m<0?-m:m}m<d{d=m;v=$1}END {print v} ' ../smd.txt >> times.txt
done 
echo "done with times.txt"

#put steps and time from smd.out into a file for easy processing
awk  ' /NSTEP/ { print $3,$6 }; $1=="A" && $2=="V" {exit 0}' ../smd.out >> stepsandtime.txt

cat times.txt | while read line || [[ -n $line ]] ; do
#need to go into smd.out and get frame when ps is closest to each times.txt
awk -v c=2 -v t=$line 'NR==1{d=$c-t;d=d<0?-d:d;v=$c;next}{m=$c-t;m=m<0?-m:m}m<d{d=m;v=$c}END {print v} ' stepsandtime.txt >> roundedtimes.txt
done

#convert ps to frames
awk '{print $1/(10)}' roundedtimes.txt >> frames.txt

dist_array=( $(seq 1.65 .1 3.65 ))
readarray -t  frames_array < frames.txt
for index in "${!dist_array[@]}"
do
cpptrajinput="cpptraj."${dist_array[index]}".in"
cat >$cpptrajinput <<EOF
parm ../../../../../../tleap/sys.parm7
trajin ../smd.nc ${frames_array[index]} ${frames_array[index]} 1 
autoimage
trajout ${dist_array[index]}.rst7 restart
EOF
echo "done making $cpptrajinput"
done

for index in "${!dist_array[@]}"
do
cpptraj -i cpptraj.${dist_array[index]}.in	
done

cd ..


