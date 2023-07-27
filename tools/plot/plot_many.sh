#!/bin/bash
set -e

# An example script for iterating over and plotting many files
# Derived from utils/scripts/do_many.sh
# This is intended to be copied into a working dir and edited directly. 

# Whitelist/Blacklist strings from target directories
    #eg whitelist=("system1" "system2")
whitelist=()
blacklist=()

# Paths to iterate through
    #eg targets="/paths/that/*/contain/wildcards_or_files"
targets=""

# Function for your desired operations. Will be run in each destination
commands() {
    target=$1
    label=$2
    xtalval=$(tail -1 "xtal.dat" | awk '{print $2}')

    echo "
    plot\\
    \"$target\" u 1:2 every 1 w l lw 1 title \"$label\"
    " >> plot.gnu
}

# Source utility functions
source utils/scripts/general/functions.sh

# Start of the script

script=$(realpath "$0")
script_gnu=$(echo "$SCRIPT" | sed 's/_/\\\\_/g')

echo "
set term x11 size 1280,720
set multiplot layout 4,4 rowsfirst
set lmargin 1
set rmargin 1
set tmargin 1
set bmargin 1.2
set label 1 \"$SCRIPT_gnu\" at screen 0.5, screen 0.99 center
set label 2 \"Distance (A)\" at screen 0.5, screen 0.01 center
set label 3 \"Count\" at screen 0.01, screen 0.5 center rotate by 90
set key t r
unset ytics
#set logscale y

" > plot.gnu

for target in $targets; do
    echo "Starting $target"
    if verify_target $target $whitelist $blacklist; then
        label=$(label_target $target $targets)
        commands $target $label
    else
        echo "Skipping $target."
    fi
done

echo "
pause -1" >> plot.gnu

gnuplot plot.gnu