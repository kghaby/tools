#!/usr/bin/env python3
#TODO: use histogram script for histo instead for more control over params. as in, take histo as input 
#TODO: fix labeling
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import argparse
import sys

# Constants
KB = 0.0019872041  # Boltzmann constant in kcal/(mol*K)
TEMP = 310  # Temperature in K

def load_data(path):
    try:
        return np.loadtxt(path)[:, 1]
    except Exception as e:
        print(f"Error loading data from {path}: {e}")
        sys.exit(1)

def load_xtal_data(path):
    try:
        return np.loadtxt(path)[1]
    except Exception as e:
        print(f"Error loading xtal data from {path}: {e}")
        sys.exit(1)

def get_label(path1):
    # Check from file to parent directories for distinguishing name
    for p1_part in zip(path1.parts[::-1]):
            return p1_part
    return 'data'  # Default label

def main(args):
    print("Loading data...")
    x = load_data(args.x_data)

    print("Calculating PMF...")
    try:
        H, xedges = np.histogram(x, bins=30)
        G = -KB * TEMP * np.log(H / np.sum(H))
        G = G - np.min(G)
        Gmasked = np.ma.masked_invalid(G)
    except Exception as e:
        print(f"Error processing data: {e}")
        sys.exit(1)

    print("Generating plot...")
    plt.rcParams.update({'font.size': 24})
    my_dpi = 96
    fig = plt.figure(figsize=(1280/my_dpi, 960/my_dpi), dpi=my_dpi)
    x_midpoints = (xedges[:-1] + xedges[1:]) / 2.0
    plt.plot(x_midpoints,Gmasked)
    plt.xlim(args.x_range)
    plt.xlabel(get_label(args.x_data))
    plt.ylabel('Energy (kcal/mol)')

    if args.x_xtal:
        print("Loading and plotting xtal data...")
        x_xtal = load_xtal_data(args.x_xtal)
        plt.plot(x_xtal,0, s=100, marker="d", label="Xtal", color="xkcd:maroon") #make this a line
        plt.legend(loc='upper right')

    plt.show()
    output_filename = f"{get_label(args.x_data)}.png"
    fig.savefig(output_filename)
    print(f"Saved plot as {output_filename}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='1D PMF plotter.')
    parser.add_argument('x_data', type=Path, help='Path to x data. Loads second column.')
    parser.add_argument('--x_xtal', type=Path, help='Optional path to x xtal data.')
    parser.add_argument('--x_range', nargs=2, type=float, default=None, help='Optional x range.')
    args = parser.parse_args()

    main(args)

