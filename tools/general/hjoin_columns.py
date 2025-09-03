#!/usr/bin/env python3
import argparse
import pandas as pd

def combine_data(file1, file2, output_file, log_file, col1_idx, col2_idx):
    df1 = pd.read_csv(file1, sep='\s+', comment="#")
    df2 = pd.read_csv(file2, sep='\s+', comment="#")

    frame_col1 = df1.columns[0]
    frame_col2 = df2.columns[0]

    data_col1 = df1.columns[col1_idx]
    data_col2 = df2.columns[col2_idx]

    merged = pd.merge(
        df1[[frame_col1, data_col1]],
        df2[[frame_col2, data_col2]],
        left_on=frame_col1,
        right_on=frame_col2,
        how="inner"
    ).drop(columns=[frame_col2])

    merged.to_csv(output_file, index=False, sep="\t")

    with open(log_file, "w") as f:
        f.write(f"Combined {file1} col {data_col1} and {file2} col {data_col2} into {output_file}\n")

def main():
    p = argparse.ArgumentParser(description="Horizontally merge two columns into a new file (keeping Frames from the first file)")
    p.add_argument("-i1", required=True, help="Path to first input file")
    p.add_argument("-i2", required=True, help="Path to second input file")
    p.add_argument("-o", default="hjoined_data.dat", help="Output file name")
    p.add_argument("-l", default="hjoin.log", help="Log file name")
    p.add_argument("-c1", type=int, default=1, help="Column index from file1 (0-based, default=1)")
    p.add_argument("-c2", type=int, default=1, help="Column index from file2 (0-based, default=1)")
    a = p.parse_args()

    combine_data(a.i1, a.i2, a.o, a.l, a.c1, a.c2)

if __name__ == "__main__":
    main()

