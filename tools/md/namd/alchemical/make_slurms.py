#!/usr/bin/env python3

"""
Generate SLURM scripts per *conf file in BFEE_dir using user-specified prefix.
"""

from __future__ import annotations
import os, sys, re

BFEE_dir = "BFEE"  # relative to script

_slurm_template = """\
#!/bin/bash
##SBATCH --dependency=afterok:1
#SBATCH --mail-user=kyleghaby@uchicago.edu
#SBATCH --mail-type=ALL
#SBATCH --job-name={job_name}
#SBATCH --time=48:00:00
#SBATCH --account=pi-roux
#SBATCH --partition=beagle3
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --gpus-per-task=1
#SBATCH --cpus-per-task=8
##SBATCH --exclude=beagle3-0015,beagle3-0017,beagle3-0003,beagle3-0012,beagle3-0009,beagle3-0019,beagle3-0006,beagle3-0004,beagle3-0005,beagle3-0010,beagle3-0028,beagle3-0022,beagle3-0007,beagle3-0011
#SBATCH --constraint=a100

module unload cuda openmpi gcc
module load namd/3.0.1-multicore-cuda

namd3 +p8 +setcpuaffinity +idlepoll +devices 0 {step_name}.conf > {step_name}.log
"""

def find_conf_files(root: str):
    for dirpath, _, filenames in os.walk(root):
        for fn in filenames:
            if fn.endswith(".conf"):
                yield os.path.join(dirpath, fn)

def make_slurm(path: str, prefix: str):
    dir_, fname = os.path.split(path)
    step_name = fname.rsplit(".conf", 1)[0]
    job_name = f"{prefix}_{step_name}"
    slurm_contents = _slurm_template.format(job_name=job_name, step_name=step_name)
    slurm_path = os.path.join(dir_, f"{step_name}.slurm")

    #if os.path.exists(slurm_path):
    #    print(f"SKIPPED (exists): {slurm_path}")
    #    return

    with open(slurm_path, "w") as f:
        f.write(slurm_contents)
    print(f"MADE: {slurm_path}")

def main():
    root = os.path.abspath(BFEE_dir)
    if not os.path.isdir(root):
        print(f"BFEE_dir does not exist: {root}", file=sys.stderr)
        sys.exit(1)

    prefix = input("Enter system prefix (e.g. b4a9 for BTK_4A9): ").strip()
    if not prefix:
        print("No prefix provided", file=sys.stderr)
        sys.exit(1)

    for conf_path in find_conf_files(root):
        try:
            make_slurm(conf_path, prefix)
        except Exception as e:
            print(f"Error processing {conf_path}: {e}", file=sys.stderr)

if __name__ == "__main__":
    main()

