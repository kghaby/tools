#!/usr/bin/env python3
import argparse
import numpy as np
from pathlib import Path

def compute_overlap(file1, file2, col1, col2, bins):
    # Load data
    data1 = np.loadtxt(file1, usecols=(col1 - 1))
    data2 = np.loadtxt(file2, usecols=(col2 - 1))

    # Compute bin edges
    bin_edges = np.histogram_bin_edges(np.concatenate([data1, data2]), bins=bins)

    # Compute histograms
    hist1, _ = np.histogram(data1, bins=bin_edges)
    hist2, _ = np.histogram(data2, bins=bin_edges)

    # Compute overlap
    area = np.minimum(hist1, hist2).sum()
    fraction = area / len(data2)

    return fraction

def main():
    parser = argparse.ArgumentParser(description='Compute overlap between two histograms. Takes raw data as input.')
    parser.add_argument('-i1', required=True, help='First input file')
    parser.add_argument('-i2', required=True, help='Second input file')
    parser.add_argument('-o', default='', help='Output file')
    parser.add_argument('-col1', type=int, default=1, help='Column containing the data in the first file')
    parser.add_argument('-col2', type=int, default=1, help='Column containing the data in the second file')
    parser.add_argument('-bins', type=int, default=10, help='Number of bins for the histogram')
    parser.add_argument('-label1', default=None, help='Label for the first file')
    parser.add_argument('-label2', default=None, help='Label for the second file')
    args = parser.parse_args()

    # Compute overlap
    overlap = compute_overlap(args.i1, args.i2, args.col1, args.col2, args.bins)

    # Determine labels
    label1 = args.label1 if args.label1 else args.i1
    label2 = args.label2 if args.label2 else args.i2

    # Save to file if output file provided, else print to stdout
    output_string = f"{label1}\t{label2}\t{overlap}"
    if args.o:
        with open(args.o, 'w') as f:
            f.write(output_string + '\n')
    else:
        print(output_string)

if __name__ == "__main__":
    main()
