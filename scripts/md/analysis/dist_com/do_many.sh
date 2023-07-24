#!/bin/bash
set -e 
analysis_dir="dist_com"
int="0.1"

for dir in /beagle3/roux/kyleghaby/kininhibs/main/*/md/13/*/prod/analysis/${analysis_dir}; do
	cd $dir	
	echo "Starting $dir"
	./data.sh
	/beagle3/roux/kyleghaby/kininhibs/main/code/histogram -i data.dat -col 2  -o data.histo -int $int
done
