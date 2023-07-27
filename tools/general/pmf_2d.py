#!/usr/bin/python3
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

def get_label(path1, path2):
    # Check from file to parent directories for distinguishing name
    for p1_part, p2_part in zip(path1.parts[::-1], path2.parts[::-1]):
        if p1_part != p2_part:
            return p1_part
    return 'data'  # Default label

def main(args):
    print("Loading data...")
    # Load data
    x = load_data(args.x_data)
    y = load_data(args.y_data)

    print("Calculating PMF...")
    # Process data
    try:
        H, xedges, yedges = np.histogram2d(x, y, bins=100)
        H = np.rot90(H)
        H = np.flipud(H)
        G = -KB * TEMP * np.log(H / np.sum(H))
        G = G - np.min(G)
        Gmasked = np.ma.masked_invalid(G)
    except Exception as e:
        print(f"Error processing data: {e}")
        sys.exit(1)

    print("Generating plot...")
    # Plot
    plt.rcParams.update({'font.size': 24})
    my_dpi = 96
    fig = plt.figure(figsize=(1280/my_dpi, 960/my_dpi), dpi=my_dpi)
    plt.pcolormesh(xedges, yedges, Gmasked, cmap='jet_r')
    plt.xlim(args.x_range)
    plt.ylim(args.y_range)
    plt.xlabel(get_label(args.x_data, args.y_data))
    plt.ylabel(get_label(args.y_data, args.x_data))
    cbar = plt.colorbar()
    cbar.ax.set_ylabel('kcal/mol')

    if args.x_xtal and args.y_xtal:
        print("Loading and plotting xtal data...")
        x_xtal = load_xtal_data(args.x_xtal)
        y_xtal = load_xtal_data(args.y_xtal)
        plt.scatter(x_xtal, y_xtal, s=100, marker="d", label="Xtal", color="xkcd:maroon")
        plt.legend(loc='upper right')

    plt.show()
    output_filename = f"{get_label(args.x_data, args.y_data)}-{get_label(args.y_data, args.x_data)}.png"
    fig.savefig(output_filename)
    print(f"Saved plot as {output_filename}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='2D PMF plotter.')
    parser.add_argument('x_data', type=Path, help='Path to x data.')
    parser.add_argument('y_data', type=Path, help='Path to y data.')
    parser.add_argument('--x_xtal', type=Path, help='Optional path to x xtal data.')
    parser.add_argument('--y_xtal', type=Path, help='Optional path to y xtal data.')
    parser.add_argument('--x_range', nargs=2, type=float, default=None, help='Optional x range.')
    parser.add_argument('--y_range', nargs=2, type=float, default=None, help='Optional y range.')
    args = parser.parse_args()

    main(args)

