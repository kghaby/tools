#!/usr/bin/env python3
import argparse
import numpy as np
from pathlib import Path

def compute_pmf(histogram_data, temperature, normalize=True):
    kB = 0.0019872041  # Boltzmann constant in kcal/(mol*K)
    bin_centers, counts = histogram_data[:,0], histogram_data[:,1]
    probability = counts / np.sum(counts)
    pmf = -kB * temperature * np.log(probability)
    pmf -= np.min(pmf) if normalize else 0
    return bin_centers, pmf

def main():
    parser = argparse.ArgumentParser(description='Compute PMF from histogram data.')
    parser.add_argument('-i', required=True, help='Input histogram file')
    parser.add_argument('-o', default='', help='Output PMF file')
    parser.add_argument('-temp', type=float, default=300, help='Temperature in Kelvin')
    parser.add_argument('-normalize', action='store_true', default='True', help='Normalize PMF so the minimum is 0')
    parser.add_argument('-v', action='store_true', help='Print detailed information during the process')
    args = parser.parse_args()

    histogram_data = np.loadtxt(args.i)

    bin_centers, pmf = compute_pmf(histogram_data, args.temp, args.normalize)

    output_file = args.o if args.o else Path(args.i).with_suffix('.pmf')
    np.savetxt(output_file, np.column_stack([bin_centers, pmf]), fmt='%.4f')

    if args.v:
        print(f"PMF calculated at T = {args.temp} K")
        print(f"PMF saved to {output_file}")

if __name__ == "__main__":
    main()

