#!/usr/bin/env python3
import argparse
from datetime import datetime
import pandas as pd

def combine_data(files, columns, output_file, log_file, no_frame_col):
    if len(files) != len(columns):
        raise ValueError("Number of files must match number of column indices")
    
    if len(files) < 2:
        raise ValueError("At least 2 files are required")
    
    # Read all files
    dfs = []
    for file_path in files:
        dfs.append(pd.read_csv(file_path, sep=r"\s+", header=0))
    
    if no_frame_col:
        # Files don't have frame columns - assume they have the same number of rows
        # and we're merging by row index
        merged_data = {}
        
        for i, (df, file_path, col_idx) in enumerate(zip(dfs, files, columns)):
            if col_idx >= len(df.columns):
                raise ValueError(f"Column index {col_idx} out of bounds for file {file_path} (has {len(df.columns)} columns)")
            
            col_name = f"{file_path}_col{col_idx}"
            merged_data[col_name] = df.iloc[:, col_idx].values
        
        # Create DataFrame from combined data
        merged = pd.DataFrame(merged_data)
        
    else:
        # Files have frame columns - merge using the first file's frame column
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
    log_lines.append(f"  Frame columns: {'excluded' if no_frame_col else 'included'}")
    
    log_message = "\n".join(log_lines)
    
    with open(log_file, "w") as f:
        f.write(log_message)
    
    print(log_message)

def main():
    p = argparse.ArgumentParser(description="Horizontally merge multiple columns from multiple files into a new file")
    p.add_argument("-i", "--input", nargs="+", required=True, 
                  help="Paths to input files (space-separated)")
    p.add_argument("-c", "--columns", nargs="+", type=int, default=None,
                  help="Column indices for each file (0-based, space-separated). "
                       "If not specified, uses column 0 for all files.")
    p.add_argument("-o", "--output", default="hjoined_data.dat", 
                  help="Output file name")
    p.add_argument("-l", "--log", default="hjoin.log", 
                  help="Log file name")
    p.add_argument("--nox", action="store_true",
                  help="Files don't have frame columns (merge by row index)")
    
    a = p.parse_args()
    
    # Set default columns if not provided
    if a.columns is None:
        # Use column 0 if no frame columns, column 1 if frame columns present
        columns = [0 if a.nox else 1] * len(a.input)
    else:
        columns = a.columns
    
    # Validate input
    if len(a.input) != len(columns):
        raise ValueError(f"Number of files ({len(a.input)}) must match number of column indices ({len(columns)})")
    
    combine_data(a.input, columns, a.output, a.log, a.nox)

if __name__ == "__main__":
    main()