#!/usr/bin/env python3
import argparse
import numpy as np

#eg ./histogram.py -i datafile -col 2 -max 10 -min 0 -int 1 -freq -o results.out

def main():
    parser = argparse.ArgumentParser(description='Prepare data for histogram.')
    parser.add_argument('-i', required=True, help='Input file containing the data')
    parser.add_argument('-o', default='', help='Output file')
    parser.add_argument('-col', type=int, default=1, help='Column containing the data')
    parser.add_argument('-min', type=float, help='Min for the histogram')
    parser.add_argument('-max', type=float, help='Max for the histogram')
    parser.add_argument('-int', type=float, default=1, help='Interval for the histogram')
    parser.add_argument('-freq', action='store_true', help='Output frequency instead of occurrence')
    parser.add_argument('-cumul', action='store_true', help='Output cumulative distribution')
    parser.add_argument('-v', action='store_true', help='Print detailed information during the process')
    args = parser.parse_args()

    # Load data from the file
    data = np.loadtxt(args.i, usecols=(args.col - 1))

    # If min or max not specified, use min/max from data
    min_val = np.min(data) if args.min is None else args.min
    max_val = np.max(data) if args.max is None else args.max

    # Compute histogram
    bins = np.arange(min_val, max_val, args.int)
    hist, bin_edges = np.histogram(data, bins=bins, density=args.freq)

    # If cumulative, compute cumulative distribution
    if args.cumul:
        hist = np.cumsum(hist)
        if args.freq:
            hist /= hist[-1]

    # Prepare output filename
    output_file = args.o if args.o else args.i + '.histo'

    # Save histogram to file
    np.savetxt(output_file, np.column_stack([bin_edges[:-1], hist]), fmt='%.4f')

    if args.v:
        print(f"Total number of data = {len(data)}")
        print(f"Histogram saved to {output_file}")

if __name__ == "__main__":
    main()
