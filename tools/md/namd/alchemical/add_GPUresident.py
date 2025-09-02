#!/usr/bin/env python3

"""
Idempotent insertion of 'GPUresident on' in *conf files under `BFEE_dir`.
"""

from __future__ import annotations
import os, io, re, sys

BFEE_dir = "BFEE" # relative to script location

_anchor_re = re.compile(r'^\s*(parameters|coordinates|structure)\b', re.IGNORECASE)  # anchor line check
_gpu_any_re = re.compile(r'^\s*GPUresident\b', re.MULTILINE)                         # existence check
_gpu_off_re = re.compile(r'^\s*GPUresident\s+off\b', re.IGNORECASE | re.MULTILINE)   # off check

def find_conf_files(root: str):
    for dirpath, _, filenames in os.walk(root):
        for fn in filenames:
            if fn.endswith("conf"):
                yield os.path.join(dirpath, fn)

def read_text(path: str) -> str:
    with open(path, 'rb') as f:
        raw = f.read()
    return raw.decode('utf-8')

def write_text_if_changed(path: str, original: str, updated: str) -> bool:
    if updated == original:
        return False
    with open(path, 'w', encoding='utf-8') as f:
        f.write(updated)
    return True

def insert_after_last_anchor(lines: list[str]) -> list[str]:
    # find last index where an anchor line begins; insert GPUresident on after that line
    last_idx = -1
    for i, line in enumerate(lines):
        if _anchor_re.match(line):
            last_idx = i
    insert_line = "GPUresident on\n"
    if last_idx >= 0:
        lines.insert(last_idx + 1, insert_line)
    else:
        # no anchors. put first
        lines.insert(0, insert_line)
    return lines

def process_file(path: str):
    print(f"FILE: {path}")

    # Exceptions
    if path.endswith("000.2_eq_ligandOnly.conf"):
        print("\tSkipping")
        return

    text = read_text(path)

    if _gpu_any_re.search(text):
        if _gpu_off_re.search(text):
            print("\tGPUresident exists but is OFF; no changes made.")
        else:
            print("\tGPUresident exists; no changes made.")
        return

    lines = text.splitlines(keepends=True)
    updated_lines = insert_after_last_anchor(lines[:]) 
    updated = "".join(updated_lines)

    changed = write_text_if_changed(path, text, updated)
    if changed:
        print("\tInserted 'GPUresident on'.")
    else:
        print("\tNo changes")

def main():
    root = os.path.abspath(BFEE_dir)
    if not os.path.isdir(root):
        print(f"BFEE_dir does not exist: {root}", file=sys.stderr)
        sys.exit(1)

    for conf_path in find_conf_files(root):
        try:
            process_file(conf_path)
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)

if __name__ == "__main__":
    main()


