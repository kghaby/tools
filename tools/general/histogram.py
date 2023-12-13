#!/usr/bin/env python3
import argparse
import numpy as np
from pathlib import Path

def compute_histogram(data, bins, density=False, cumulative=False):
    hist, bin_edges = np.histogram(data, bins=bins, density=density)
    if cumulative:
        hist = np.cumsum(hist)
        if density:
            hist /= hist[-1]
    return bin_edges, hist

def main():
    parser = argparse.ArgumentParser(description='Prepare data for histogram.')
    parser.add_argument('-i', required=True, help='Input file containing the data')
    parser.add_argument('-o', default='', help='Output file')
    parser.add_argument('-col', type=int, default=0, help='Column containing the data. Indexing starts at 0.')
    parser.add_argument('-min', type=float, help='Min for the histogram')
    parser.add_argument('-max', type=float, help='Max for the histogram')
    parser.add_argument('-bins', type=int, default=100, help='Number of bins for the histogram')
    parser.add_argument('-binsize', type=float, default=None, help='Bin size for the histogram. Will override -bins!')
    parser.add_argument('-freq', action='store_true', help='Output frequency instead of occurrence')
    parser.add_argument('-cumul', action='store_true', help='Output cumulative distribution')
    parser.add_argument('-v', action='store_true', help='Print detailed information during the process')
    args = parser.parse_args()

    # Load data from the file
    data = np.loadtxt(args.i, usecols=(args.col))

    # If min or max not specified, use min/max from data
    min_val = np.min(data) if args.min is None else args.min
    max_val = np.max(data) if args.max is None else args.max

    # Handle bins and binsize
    if args.binsize is not None:
        bin_range = np.abs(max_val - min_val)
        bins = int(np.ceil(bin_range / args.binsize))+1
    else:
        bins = args.bins
    print(bins)
    # Compute histogram
    bin_edges, hist = compute_histogram(data, bins=bins, density=args.freq, cumulative=args.cumul)

    # Calculate bin centers
    bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2

    # Prepare output filename
    output_file = args.o if args.o else Path(args.i).with_suffix('.histo')

    # Save histogram to file
    np.savetxt(output_file, np.column_stack([bin_centers, hist]), fmt='%.4f')


    if args.v:
        print(f"Total number of data = {len(data)}")
        print(f"Histogram bins = {len(bin_edges) - 1}")
        print(f"Histogram range = [{min_val}, {max_val}]")
        print(f"Histogram saved to {output_file}")

if __name__ == "__main__":
    main()


