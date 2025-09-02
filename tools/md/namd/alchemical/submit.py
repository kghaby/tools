#!/usr/bin/env python3

# NOT USED


import subprocess
from pathlib import Path

# user-defined filters
whitelist = ["001","002","003","004"]  # run only matching (sub)steps; [] for all
blacklist = []  # skip matching (sub)steps

# mapping of substep IDs to substep descriptors
substep_map = {
    "001.1": "fep_backward",
    "001.2": "fep_forward",
    "002.1": "ti_backward",
    "002.2": "ti_forward",
    "003.1": "fep_backward",
    "003.2": "fep_forward",
    "004.1": "ti_backward",
    "004.2": "ti_forward",
}
# mapping of step IDs to step descriptors
step_map = {
    "001": "MoleculeBound",
    "002": "RestraintBound",
    "003": "MoleculeUnbound",
    "004": "RestraintUnbound",
}

# specify BFEE dir, which should be a sibling of submit.py
root = (Path(__file__).parent / "BFEE").resolve() 

prev_job_id = "1"
prev_job_name = ""

def make_slurm_script(name, dep):
    return f"""#!/bin/bash
#SBATCH --dependency=afterok:{dep}
#SBATCH --mail-user=kyleghaby@uchicago.edu
#SBATCH --mail-type=ALL
#SBATCH --job-name={name}
#SBATCH --time=48:00:00
#SBATCH --account=pi-roux
#SBATCH --partition=beagle3
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --gpus-per-node=2
#SBATCH --cpus-per-task=15

module unload cuda openmpi gcc
module load namd/3.0.1-multicore-cuda

srun namd3 +p15 +pmepes 7 +setcpuaffinity +devices 0,1 {name}.conf > {name}.log
"""

for substep_num, substep_desc in substep_map.items():
    substep = f"{substep_num}_{substep_desc}" 
    
    if whitelist and not any(w in substep for w in whitelist):
        continue
    if any(b in substep for b in blacklist):
        continue
    
    step_num = substep_num.split('.')[0]
    if prev_job_name.startswith(f"{step_num}.{int(substep_num.split('.')[1])-1}"):
        extra_message = f", dependent on {prev_job_name}"
    else:
        prev_job_id = 1 
        prev_job_name = ""
        extra_message = ""
        
    subdir = root / f"{step_num}_{step_map[step_num]}"
    slurm_path = subdir / f"{substep}.slurm"
    slurm_path.write_text(make_slurm_script(substep, prev_job_id)) 
    res = subprocess.check_output(["sbatch", slurm_path.name], cwd=subdir, text=True)
    jid = res.strip().split()[-1]
    print(f"Submitted {slurm_path.name}, id={jid}{extra_message}\n")
    prev_job_id = jid
    prev_job_name = substep
