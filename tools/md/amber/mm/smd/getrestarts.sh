#!/bin/bash

#invoke the script with the -h flag for usage details: ./script.sh -h

function print_help {
    echo "Usage: ./script.sh -i INPUT_DIR -o OUTPUT_DIR"
    echo "Arguments:"
    echo "  -i INPUT_DIR    The directory containing the input files"
    echo "  -o OUTPUT_DIR   The directory where the output files will be written"
    echo "  -h              Display help"
    exit 1
}

while getopts "i:o:h" OPTION; do
    case "$OPTION" in
        i) INPUT_DIR="$OPTARG" ;;
        o) OUTPUT_DIR="$OPTARG" ;;
        h) print_help ;;
        *) print_help ;;
    esac
done

if [[ -z "$INPUT_DIR" || -z "$OUTPUT_DIR" ]]; then
    echo "Error: Both input (-i) and output (-o) directories must be specified"
    print_help
    exit 1
fi

if [[ ! -d "$INPUT_DIR" ]]; then
    echo "Error: Input directory $INPUT_DIR does not exist"
    exit 1
fi

if [[ ! -d "$OUTPUT_DIR" ]]; then
    mkdir -p "$OUTPUT_DIR"
fi

function execute_awk_operations {
    awk_file="$1"
    begin="$2"
    step="$3"
    end="$4"
    for i in $(seq $begin $step $end); do
        awk -v c=2 -v t=$i 'NR==1{d=$c-t;d=d<0?-d:d;v=$1;next}{m=$c-t;m=m<0?-m:m}m<d{d=m;v=$1}END {print v}' "$INPUT_DIR/$awk_file"
    done
}

function generate_cpptraj_files {
    dist_begin="$1"
    dist_end="$2"
    dist_step="$3"
    readarray -t frames_array < "$OUTPUT_DIR/frames.txt"
    for dist in $(seq $dist_begin $dist_step $dist_end); do
        cpptrajinput="$OUTPUT_DIR/cpptraj.$dist.in"
        cat > "$cpptrajinput" << EOF
    parm $INPUT_DIR/tleap/sys.parm7
    trajin $INPUT_DIR/smd.nc ${frames_array[index]} ${frames_array[index]} 1 
    autoimage
    trajout $dist.rst7 restart
EOF
        echo "Generated $cpptrajinput"
    done
}

execute_awk_operations smd.txt 16.5 1 36.5 > "$OUTPUT_DIR/times.txt"
echo "Processed times.txt"

awk ' /NSTEP/ { print $3,$6 }; $1=="A" && $2=="V" {exit 0}' "$INPUT_DIR/smd.out" > "$OUTPUT_DIR/stepsandtime.txt"
echo "Processed stepsandtime.txt"

execute_awk_operations stepsandtime.txt > "$OUTPUT_DIR/roundedtimes.txt"
echo "Processed roundedtimes.txt"

awk '{print $1/10}' "$OUTPUT_DIR/roundedtimes.txt" > "$OUTPUT_DIR/frames.txt"
echo "Converted ps to frames"

generate_cpptraj_files 1.65 3.65 0.1
echo "Generated cpptraj files"

cd "$OUTPUT_DIR"
for dist in $(seq 1.65 0.1 3.65); do
    cpptraj -i cpptraj.$dist.in	
done

echo "Script execution completed"

