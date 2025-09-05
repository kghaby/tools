#!/usr/bin/env python3
import argparse
from datetime import datetime
import pandas as pd

def get_file_info(file_path):
    """Determine if file has header and read appropriate column names"""
    with open(file_path, 'r') as f:
        first_line = f.readline().strip()
    
    has_header = first_line.startswith('#')
    
    if has_header:
        # Read just the header line to get column names
        df_header = pd.read_csv(file_path, sep=r"\s+", header=0, comment='#', nrows=0)
        column_names = list(df_header.columns)
    else:
        # Read the file to determine number of columns, then generate names
        df_temp = pd.read_csv(file_path, sep=r"\s+", header=None, nrows=1)
        column_names = [f"col{i}" for i in range(len(df_temp.columns))]
    
    return has_header, column_names

def combine_data(files, columns, output_file, log_file, no_frame_col):
    if len(files) != len(columns):
        raise ValueError("Number of files must match number of column indices")
    
    if len(files) < 2:
        raise ValueError("At least 2 files are required")
    
    # Get file information first
    file_info = []
    dfs = []
    for file_path in files:
        has_header, column_names = get_file_info(file_path)
        
        # Read the actual data
        if has_header:
            df = pd.read_csv(file_path, sep=r"\s+", header=0, comment='#')
        else:
            df = pd.read_csv(file_path, sep=r"\s+", header=None)
        
        file_info.append({
            'path': file_path,
            'has_header': has_header,
            'column_names': column_names
        })
        dfs.append(df)
    
    if no_frame_col:
        # Merge by row index - no frame columns
        series_list = []
        
        for i, (df, info, col_idx) in enumerate(zip(dfs, file_info, columns)):
            if col_idx >= len(df.columns):
                raise ValueError(f"Column index {col_idx} out of bounds for file {info['path']} (has {len(df.columns)} columns)")
            
            # Get base column name
            base_col_name = info['column_names'][col_idx]
            col_name = f"{base_col_name}_f{i+1}"
            
            series = df.iloc[:, col_idx].copy()
            series.name = col_name
            series_list.append(series)
        
        merged = pd.concat(series_list, axis=1)
        
    else:
        # Merge using frame columns
        primary_key_col = "#Frame"
        merged_data = {}
        column_mapping = {}  # Track original column names to unique output names
        
        # Process each file
        for i, (df, info, col_idx) in enumerate(zip(dfs, file_info, columns)):
            if col_idx >= len(df.columns):
                raise ValueError(f"Column index {col_idx} out of bounds for file {info['path']} (has {len(df.columns)} columns)")
            
            base_col_name = info['column_names'][col_idx]
            unique_col_name = f"{base_col_name}_f{i+1}"
            column_mapping[(i, col_idx)] = unique_col_name
            
            # Get frame column (first column) and data column
            frame_data = df.iloc[:, 0].values
            col_data = df.iloc[:, col_idx].values
            
            # Store data by frame value
            for frame_val, data_val in zip(frame_data, col_data):
                if frame_val not in merged_data:
                    merged_data[frame_val] = {}
                merged_data[frame_val][unique_col_name] = data_val
        
        # Convert to DataFrame
        frames = sorted(merged_data.keys())
        all_columns = set()
        for frame_data in merged_data.values():
            all_columns.update(frame_data.keys())
        
        # Create DataFrame
        merged = pd.DataFrame(index=frames, columns=sorted(all_columns))
        for frame_val, data_dict in merged_data.items():
            for col_name, data_val in data_dict.items():
                merged.loc[frame_val, col_name] = data_val
        
        # Reset index and rename frame column
        merged = merged.reset_index()
        merged = merged.rename(columns={'index': primary_key_col})
    
    # Save the combined data
    merged.to_csv(output_file, index=False, sep="\t", header=True)
    
    # Log message
    log_lines = [f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Combined data from multiple files:"]
    for i, info in enumerate(file_info):
        col_idx = columns[i]
        base_col_name = info['column_names'][col_idx]
        unique_col_name = f"{base_col_name}_f{i+1}"
        
        if info['has_header']:
            log_lines.append(f"  File {i+1}: {info['path']} (column {col_idx} - '{base_col_name}' -> '{unique_col_name}')")
        else:
            log_lines.append(f"  File {i+1}: {info['path']} (column {col_idx} - generated '{base_col_name}' -> '{unique_col_name}')")
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
            print("Using column 0 for all files (--nox specified)")
        else:
            columns = [1] * len(a.inputs)
            print("Using column 1 for all files (default for files with frame columns)")
    else:
        columns = a.cols
    
    # Validate input
    if len(a.inputs) != len(columns):
        raise ValueError(f"Number of files ({len(a.inputs)}) must match number of column indices ({len(columns)})")
    
    combine_data(a.inputs, columns, a.output, a.log, a.nox)

if __name__ == "__main__":
    main()