#!/bin/bash

#put the header into smd.txt
rm -f smd.txt
head -3 smd.1.txt > smd.txt

#chop of tail and head for each smd.txt
for i in {1..8}
do
head -n -3 smd.$i.txt > notail.$i.txt.tmp
tail -n +4 notail.$i.txt.tmp > notailorhead.$i.txt.tmp
echo "$i's old frst: $(head -1 notailorhead.$i.txt.tmp)"
echo "$i's old last: $(tail -1 notailorhead.$i.txt.tmp)"
done

#add the work to the next file 
for a in {1..7}
do
b=$((a+1))
alastwork=`tail -1 notailorhead.$a.txt.tmp | awk '{print $5}'`
blastwork=`tail -1 notailorhead.$b.txt.tmp | awk '{print $5}'`
awk -v n="$alastwork" -v CONVFMT='%.8f' '{newval=$5+n; sub(/[-+]?[0-9.]+$/,newval)}1' notailorhead.$b.txt.tmp > addedwork.$b.txt.tmp
combinedwork=`tail -1 addedwork.$b.txt.tmp | awk '{print $5}'`
echo "$alastwork + $blastwork = $combinedwork"
mv addedwork.$b.txt.tmp notailorhead.$b.txt.tmp
done

#last check
for i in {1..8}
do
echo "$i's new frst: $(head -1 notailorhead.$i.txt.tmp)"
echo "$i's new last: $(tail -1 notailorhead.$i.txt.tmp)"
done

#paste numbers into smd.txt
cat  notailorhead.*.txt.tmp >> smd.txt
echo "
Head of smd.txt:
$(head smd.txt)"
echo "
Tail of smd.txt:
$(tail smd.txt)"

#remove .tmp files
rm -f notail.*.txt.tmp
rm -f notailorhead.*.txt.tmp

