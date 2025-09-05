#!/usr/bin/env python3
import argparse
from datetime import datetime
import pandas as pd

def combine_data(files, columns, output_file, log_file):
    if len(files) != len(columns):
        raise ValueError("Number of files must match number of column indices")
    
    if len(files) < 2:
        raise ValueError("At least 2 files are required")
    
    # Read all files
    dfs = []
    for file_path in files:
        dfs.append(pd.read_csv(file_path, sep=r"\s+", header=0))
    
    # Start with the first file's frame column and selected data column
    frame_col = dfs[0].columns[0]
    merged = dfs[0][[frame_col, dfs[0].columns[columns[0]]]].copy()
    merged.columns = [frame_col, f"{files[0]}_col{columns[0]}"]
    
    # Merge remaining files
    for i in range(1, len(files)):
        df = dfs[i]
        current_frame_col = df.columns[0]
        data_col = df.columns[columns[i]]
        
        merged = pd.merge(
            merged,
            df[[current_frame_col, data_col]],
            left_on=frame_col,
            right_on=current_frame_col,
            how="inner"
        )
        
        # Drop the duplicate frame column and rename the data column
        merged = merged.drop(columns=[current_frame_col])
        merged = merged.rename(columns={data_col: f"{files[i]}_col{columns[i]}"})
    
    # Save the combined data
    merged.to_csv(output_file, index=False, sep="\t", header=True)
    
    # Log message
    log_lines = [f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Combined data from multiple files:"]
    for i, (file_path, col_idx) in enumerate(zip(files, columns)):
        log_lines.append(f"  File {i+1}: {file_path} (column {col_idx})")
    log_lines.append(f"  Output: {output_file}")
    log_lines.append(f"  Total columns combined: {len(files)}")
    
    log_message = "\n".join(log_lines)
    
    with open(log_file, "w") as f:
        f.write(log_message)
    
    print(log_message)

def main():
    p = argparse.ArgumentParser(description="Horizontally merge multiple columns from multiple files into a new file.")
    p.add_argument("-i", "--input", nargs="+", required=True, 
                  help="Paths to input files (space-separated)")
    p.add_argument("-c", "--cols", nargs="+", type=int, default=None,
                  help="Column indices for each file (0-based, space-separated). "
                       "If not specified, uses column 1 for all files.")
    p.add_argument("-o", "--output", default="hjoined_data.dat", 
                  help="Output file name")
    p.add_argument("-l", "--log", default="hjoin.log", 
                  help="Log file name")
    
    a = p.parse_args()
    
    # Set default columns if not provided
    if a.cols is None:
        columns = [1] * len(a.input)
    else:
        columns = a.cols
    
    # Validate input
    if len(a.input) != len(columns):
        raise ValueError(f"Number of files ({len(a.input)}) must match number of column indices ({len(columns)})")
    
    combine_data(a.input, columns, a.output, a.log)

if __name__ == "__main__":
    main()