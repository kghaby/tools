#!/bin/bash

function print_help {
    echo "Usage: ./script.sh -i INPUT_DIR"
    echo "Arguments:"
    echo "  -i INPUT_DIR    The directory containing the input files"
    echo "  -h              Display help"
    exit 1
}

while getopts "i:h" OPTION; do
    case "$OPTION" in
        i) INPUT_DIR="$OPTARG" ;;
        h) print_help ;;
        *) print_help ;;
    esac
done

if [[ -z "$INPUT_DIR" ]]; then
    echo "Error: Input directory (-i) must be specified"
    print_help
    exit 1
fi

if [[ ! -d "$INPUT_DIR" ]]; then
    echo "Error: Input directory $INPUT_DIR does not exist"
    exit 1
fi

function remove_headers_tails {
    local filename="$1"
    local tempname1="$2"
    local tempname2="$3"
    head -n -3 "$filename" > "$tempname1"
    tail -n +4 "$tempname1" > "$tempname2"
    echo "$(basename $filename) old first: $(head -1 $tempname2)"
    echo "$(basename $filename) old last: $(tail -1 $tempname2)"
}

function add_work_to_file {
    local file1="$1"
    local file2="$2"
    local tempname="$3"
    local alastwork=$(tail -1 "$file1" | awk '{print $5}')
    local blastwork=$(tail -1 "$file2" | awk '{print $5}')
    awk -v n="$alastwork" -v CONVFMT='%.8f' '{newval=$5+n; sub(/[-+]?[0-9.]+$/,newval)}1' "$file2" > "$tempname"
    local combinedwork=$(tail -1 "$tempname" | awk '{print $5}')
    echo "$alastwork + $blastwork = $combinedwork"
    mv "$tempname" "$file2"
}

rm -f "$INPUT_DIR/smd.txt"
head -3 "$INPUT_DIR/smd.1.txt" > "$INPUT_DIR/smd.txt"

for i in $(seq 1 8); do
    remove_headers_tails "$INPUT_DIR/smd.$i.txt" "$INPUT_DIR/notail.$i.txt.tmp" "$INPUT_DIR/notailorhead.$i.txt.tmp"
done

for a in $(seq 1 7); do
    add_work_to_file "$INPUT_DIR/notailorhead.$a.txt.tmp" "$INPUT_DIR/notailorhead.$(($a+1)).txt.tmp" "$INPUT_DIR/addedwork.$(($a+1)).txt.tmp"
done

for i in $(seq 1 8); do
    echo "$(basename $i) new first: $(head -1 $INPUT_DIR/notailorhead.$i.txt.tmp)"
    echo "$(basename $i) new last: $(tail -1 $INPUT_DIR/notailorhead.$i.txt.tmp)"
done

cat "$INPUT_DIR/notailorhead.*.txt.tmp" >> "$INPUT_DIR/smd.txt"
echo "
Head of smd.txt:
$(head $INPUT_DIR/smd.txt)"
echo "
Tail of smd.txt:
$(tail $INPUT_DIR/smd.txt)"

rm -f "$INPUT_DIR/notail.*.txt.tmp" "$INPUT_DIR/notailorhead.*.txt.tmp"

echo "Script execution completed"

