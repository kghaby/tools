#!/usr/bin/env python3
import subprocess
from pathlib import Path
from collections import OrderedDict


def run_cpptraj(
    parm: Path,
    coords: Path,
    mask: str,
    cpptraj_cmd: str = "cpptraj",
    out_prefix: str = "mask",
) -> Path:
    """
    Run cpptraj to get mask details specified by <mask>.
    """
    parm = Path(parm)
    coords = Path(coords)
    out_dat = Path(f"{out_prefix}.dat")

    # cpptraj maskout format: "#Frame AtomNum Atom ResNum Res MolNum"
    cpptraj_in = f"""parm {parm}
trajin {coords} 1 1 1
autoimage
mask "{mask}" maskout {out_dat}
run
quit
"""

    subprocess.run(
        [cpptraj_cmd],
        input=cpptraj_in,
        text=True,
        check=True,
    )

    return out_dat


def parse_maskout(maskout_path: Path):
    """
    Parse cpptraj maskout file and return:
      - sorted unique residue indices
      - sorted unique atom indices
    """
    maskout_path = Path(maskout_path)
    res_ids = OrderedDict()
    atom_ids = OrderedDict()

    with maskout_path.open() as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            # format: Frame AtomNum Atom ResNum Res MolNum
            parts = line.split()
            if len(parts) < 6:
                continue
            atom_num = int(parts[1])
            res_num = int(parts[3])
            res_name = parts[4]
            res_ids[res_num] = None
            atom_ids[atom_num] = None

    res_list = sorted(res_ids.keys())
    atom_list = sorted(atom_ids.keys())
    return res_list, atom_list


def main():
    parm = Path("BTK_4A9_l.parm7")
    coords = Path("qmmm_init.rst7")
    mask = "((:91@SG,:4A9@C1,:4A9@C15)<:5.5)&:WAT"

    maskout = run_cpptraj(parm, coords, mask)

    res_list, atom_list = parse_maskout(maskout)

    res_csv = ",".join(str(r) for r in res_list)
    atom_csv = ",".join(str(a) for a in atom_list)

    print("Residue indices:")
    print(res_csv)
    print("\nAtom indices:")
    print(atom_csv)
    
    print("\nResidue indices for VMD (0-based):")
    print(" ".join(str(r - 1) for r in res_list))
    print("\nAtom indices for VMD (0-based):")
    print(" ".join(str(a - 1) for a in atom_list))


if __name__ == "__main__":
    main()