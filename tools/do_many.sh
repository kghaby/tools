#!/bin/bash
set -e
source utils/scripts/general/functions.sh

# A template master script for performing a set of commands on a bunch of targets (files/dirs).
# This is intended to be copied into a working dir and edited directly. 

# Whitelist/Blacklist strings from target directories
    #eg whitelist=("system1" "system2")
whitelist=()
blacklist=()

# Paths to iterate through
    #eg targets="/paths/that/*/contain/wildcards_or_files"
targets=""

# Function for your desired operations. Will be run in each destination.
    # Includes some general code for convenience
commands() {
    target=$1
    label=$2
    # Navigate to the target, unless its a file
    if [[ -f $target ]]; then
        #pushd "$(dirname "$target")"
        : # avoid syntax error and return true
    elif [[ -d $target ]]; then
        pushd $target
    fi


    popd
}

# Start of the script
for target in $targets; do
    echo "Starting $target"
    if verify_target $target; then
        label=$(label_target $target $targets)
        commands $target $label
    else
        echo "Skipping $target"
    fi
done
