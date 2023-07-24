#!/bin/bash
set -e 
#runs data.sh assuming its already set up

analysis_dir="linkdist"

#whitelist=("BTK_4A9" "BTK_4B9" "BTK_4C9" "EGFR_4C9" "SRC_5YZ" "AURKA_5YZ")
whitelist=()
blacklist=()

for dir in /beagle3/roux/kyleghaby/kininhibs/main/*/md/13/unlinked/prod/analysis/${analysis_dir}; do

#get name of system
IFS='/' read -ra arrDir <<< $dir
system=$(echo "${arrDir[6]}")

#check whitelist
if (( "${#whitelist[@]}" > 0 )); then
if [[ ! " ${whitelist[*]} " =~ " ${system} " ]]; then
echo "

$system IS NOT WHITELISTED...............SKIPPING

"
continue
fi
fi

#check blacklist
if (("${#blacklist[@]}" > 0 )); then
if [[ " ${blacklist[*]} " =~ " ${system} " ]]; then
echo "

$system IS BLACKLISTED...............SKIPPING

"
continue
fi
fi

cd $dir
echo "Starting $dir"
./data.sh
done
