#!/usr/bin/env python3
import argparse
from datetime import datetime
import pandas as pd
import os

def combine_data(files, columns, output_file, log_file, no_frame_col):
    if len(files) != len(columns):
        raise ValueError("Number of files must match number of column indices")
    
    if len(files) < 2:
        raise ValueError("At least 2 files are required")
    
    # Read all files and determine if they have headers
    dfs = []
    has_headers = []
    all_headers = []
    
    for file_path in files:
        # Check if first line starts with comment character
        with open(file_path, 'r') as f:
            first_line = f.readline().strip()
        
        if first_line.startswith('#'):
            # File has header (starts with comment)
            df = pd.read_csv(file_path, sep=r"\s+", header=0, comment='#')
            has_headers.append(True)
            all_headers.append(list(df.columns))
        else:
            # File doesn't have header
            df = pd.read_csv(file_path, sep=r"\s+", header=None)
            has_headers.append(False)
            # Generate column names
            all_headers.append([f"col{i}" for i in range(len(df.columns))])
        dfs.append(df)
    
    # Extract the requested columns with proper naming
    extracted_columns = []
    column_names = []
    
    for i, (df, col_idx, headers) in enumerate(zip(dfs, columns, all_headers)):
        if col_idx >= len(df.columns):
            raise ValueError(f"Column index {col_idx} out of bounds for file {files[i]} (has {len(df.columns)} columns)")
        
        # Get the column name
        col_name = headers[col_idx]
        
        # Make column name unique if needed
        base_name = col_name
        suffix = 1
        while col_name in column_names:
            col_name = f"{base_name}_{suffix}"
            suffix += 1
        
        column_names.append(col_name)
        extracted_columns.append((df.iloc[:, col_idx], col_name))
    
    if no_frame_col:
        # Merge by row index
        merged_data = pd.concat([col for col, name in extracted_columns], axis=1)
        merged_data.columns = column_names
    else:
        # Merge using frame columns
        frame_data = []
        frame_column_name = "#Frame"
        
        for i, df in enumerate(dfs):
            if 0 >= len(df.columns):
                raise ValueError(f"File {files[i]} doesn't have a frame column")
            
            # Get frame column
            frame_col = df.iloc[:, 0]
            data_col, col_name = extracted_columns[i]
            
            # Create a DataFrame with frame and data columns
            temp_df = pd.DataFrame({
                frame_column_name: frame_col,
                col_name: data_col
            })
            frame_data.append(temp_df)
        
        # Merge all DataFrames on the frame column
        merged_data = frame_data[0]
        for i in range(1, len(frame_data)):
            merged_data = pd.merge(merged_data, frame_data[i], on=frame_column_name, how="inner")
    
    # Save the combined data with proper header format
    with open(output_file, 'w') as f:
        # Write header line
        header_line = "#" + "\t".join(merged_data.columns) + "\n"
        f.write(header_line)
        
        # Write data without header
        merged_data.to_csv(f, index=False, sep="\t", header=False)
    
    # Log message
    log_lines = [f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Combined data from multiple files:"]
    for i, (file_path, col_idx, has_header) in enumerate(zip(files, columns, has_headers)):
        col_name = column_names[i]
        if has_header:
            original_name = all_headers[i][col_idx]
            log_lines.append(f"  File {i+1}: {file_path} (column {col_idx} - '{original_name}' -> '{col_name}')")
        else:
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
            print("AMBIGUITY WARNING: Using column 0 for all files (--nox mode)")
        else:
            columns = [1] * len(a.inputs)
            print("AMBIGUITY WARNING: Using column 1 for all files (frame column mode)")
    else:
        columns = a.cols
    
    # Validate input
    if len(a.inputs) != len(columns):
        raise ValueError(f"Number of files ({len(a.inputs)}) must match number of column indices ({len(columns)})")
    
    combine_data(a.inputs, columns, a.output, a.log, a.nox)

if __name__ == "__main__":
    main()