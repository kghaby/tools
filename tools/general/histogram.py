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

def fd_bin_width(x):
    x = np.asarray(x).ravel()
    x = x[np.isfinite(x)]
    if x.size < 2:
        return 1.0
    iqr = np.subtract(*np.percentile(x, [75, 25]))
    bw = 2 * iqr * (x.size ** (-1/3))
    if bw <= 0 or not np.isfinite(bw):
        raise ValueError("IQR-based bin width is non-positive or non-finite.")
    return bw if np.isfinite(bw) and bw > 0 else 1.0

def main():
    parser = argparse.ArgumentParser(description='Prepare data for histogram.')
    parser.add_argument('-i', required=True, help='Input file containing the data')
    parser.add_argument('-o', default='', help='Output file')
    parser.add_argument('-col', type=int, default=0, help='Column containing the data. Indexing starts at 0.')
    parser.add_argument('-min', type=float, help='Min for the histogram')
    parser.add_argument('-max', type=float, help='Max for the histogram')
    parser.add_argument('-bins', type=int, default=None, help='Number of bins for the histogram. Default is determined automatically.')
    parser.add_argument('-binsize', type=float, default=None, help='Bin size for the histogram. Will override -bins!')
    parser.add_argument('-freq', action='store_true', help='Output frequency instead of occurrence')
    parser.add_argument('-cumul', action='store_true', help='Output cumulative distribution')
    parser.add_argument('-v', action='store_true', help='Print detailed information during the process')
    args = parser.parse_args()

    data = np.loadtxt(args.i, usecols=(args.col))

    min_val = np.min(data) if args.min is None else args.min
    max_val = np.max(data) if args.max is None else args.max

    if args.bins is None and args.binsize is None:
        if args.v:
            print("Determining number of bins.")
        data_fin = data[np.isfinite(data)]
        bin_width = fd_bin_width(data_fin)
        bin_range = np.abs(max_val - min_val)
        bins = int(np.ceil(bin_range / bin_width))+1
        if args.v:
            print(f"Using {bins} bins with width {bin_width:.4f}.")

    if args.binsize is not None:
        bin_range = np.abs(max_val - min_val)
        bins = int(np.ceil(bin_range / args.binsize))+1
    else:
        bins = args.bins
    
    bin_edges, hist = compute_histogram(data, bins=bins, density=args.freq, cumulative=args.cumul)

    bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2

    output_file = args.o if args.o else Path(args.i).with_suffix('.histo')
    np.savetxt(output_file, np.column_stack([bin_centers, hist]), fmt='%.4f')

    if args.v:
        print(f"Total number of data = {len(data)}")
        print(f"Histogram bins = {len(bin_edges) - 1}")
        print(f"Histogram range = [{min_val}, {max_val}]")
        print(f"Histogram saved to {output_file}")

if __name__ == "__main__":
    main()


