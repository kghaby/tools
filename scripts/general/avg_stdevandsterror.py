#!/usr/bin/env python3
import sys
import pandas as pd

# Ensure correct number of command line arguments
if len(sys.argv) != 3:
    sys.exit("Usage: ./script.py [column to analyze] [file to read from]")

# Get column number and filename from command line arguments
column = int(sys.argv[1]) - 1
filename = sys.argv[2]

# Read in file using pandas, assuming whitespace-delimited file
df = pd.read_csv(filename, delim_whitespace=True, header=None)

# Get the relevant column
data = df.iloc[:, column]

# Calculate mean, standard deviation, and standard error
mean = data.mean()
std_dev = data.std(ddof=1)  # Use Bessel's correction (n-1 in the denominator)
std_err = data.sem(ddof=1)  # Use Bessel's correction (n-1 in the denominator)

# Output results
print(f"{mean:.3f} +/- {std_dev:.3f} or {std_err:.3f}")
