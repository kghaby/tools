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
        # Create a list of Series with unique column names
        series_list = []
        
        for i, (df, file_path, col_idx) in enumerate(zip(dfs, files, columns)):
            if col_idx >= len(df.columns):
                raise ValueError(f"Column index {col_idx} out of bounds for file {file_path} (has {len(df.columns)} columns)")
            
            col_name = df.columns[col_idx]
            series = df.iloc[:, col_idx]
            
            # Check if column name already exists and rename if necessary
            existing_names = [s.name for s in series_list]
            if col_name in existing_names:
                # Add suffix to make column name unique
                suffix_num = 1
                new_name = f"{col_name}_{suffix_num}"
                while new_name in existing_names:
                    suffix_num += 1
                    new_name = f"{col_name}_{suffix_num}"
                series.name = new_name
            else:
                series.name = col_name
            
            series_list.append(series)
        
        # Create DataFrame from combined series
        merged = pd.concat(series_list, axis=1)
        
    else:
        # Files have frame columns - merge using the first column of each file as the key
        # Use the first file's first column as the primary key
        primary_key_col = dfs[0].columns[0]
        data_col_1 = dfs[0].columns[columns[0]]
        merged = dfs[0].iloc[:, [0, columns[0]]].copy()
        merged.columns = [primary_key_col, data_col_1]
        
        # Merge remaining files
        for i in range(1, len(files)):
            df = dfs[i]
            if len(df.columns) <= columns[i]:
                raise ValueError(f"Column index {columns[i]} out of bounds for file {files[i]}")
            
            # Use the first column as the merge key for each file
            key_col = df.columns[0]
            data_col = df.columns[columns[i]]
            
            # Create temporary dataframe with just the key and data columns
            temp_df = df.iloc[:, [0, columns[i]]].copy()
            temp_df.columns = [primary_key_col, data_col]
            
            merged = pd.merge(
                merged,
                temp_df,
                on=primary_key_col,
                how="inner"
            )
    
    # Save the combined data
    merged.to_csv(output_file, index=False, sep="\t", header=True)
    
    # Log message
    log_lines = [f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Combined data from multiple files:"]
    for i, (file_path, col_idx) in enumerate(zip(files, columns)):
        col_name = dfs[i].columns[col_idx]
        log_lines.append(f"  File {i+1}: {file_path} (column {col_idx} - '{col_name}')")
    log_lines.append(f"  Output: {output_file}")
    log_lines.append(f"  Total columns combined: {len(files)}")
    log_lines.append(f"  Frame columns: {'excluded' if no_frame_col else 'included'}")
    
    log_message = "\n".join(log_lines)
    
    with open(log_file, "w") as f:
        f.write(log_message)
    
    print(log_message)

def main():
    p = argparse.ArgumentParser(description="Horizontally merge multiple columns from multiple files into a new file")
    p.add_argument("-i", "--inputs", nargs="+", required=True, 
                  help="Paths to input files (space-separated)")
    p.add_argument("-c", "--cols", nargs="+", type=int, default=None,
                  help="Column indices for each file (0-based, space-separated). "
                       "If not specified, uses column 1 for files with frame columns, column 0 for files without.")
    p.add_argument("-o", "--output", default="hjoined_data.dat", 
                  help="Output file name")
    p.add_argument("-l", "--log", default="hjoin.log", 
                  help="Log file name")
    p.add_argument("--nox", action="store_true",
                  help="Files don't have frame columns (merge by row index)")
    
    a = p.parse_args()
    
    # Set default columns if not provided
    if a.cols is None:
        if a.nox:
            columns = [0] * len(a.inputs)
            print("AMBIGUITY WARNING: --nox was used but --cols (-c) was not. Using col 0 of the files.")
        else:
            columns = [1] * len(a.inputs)
            print("AMBIGUITY WARNING: --cols (-c) was not specified. Using col 1 of the files.")
    else:
        columns = a.cols
    
    # Validate input
    if len(a.inputs) != len(columns):
        raise ValueError(f"Number of files ({len(a.inputs)}) must match number of column indices ({len(columns)})")
    
    combine_data(a.inputs, columns, a.output, a.log, a.nox)

if __name__ == "__main__":
    main()