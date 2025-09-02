#!/usr/bin/env python3
import parmed as pmd

amber = pmd.load_file('../prep/BTK_4B9_u.parm7', '../prod/prod.200.rst7')

# Save a CHARMM PSF and crd file
amber.write_psf('charmm_truncated_atomtypes.psf')
#amber.save('charmm.coor') # use pdb instead (./get_pdb.sh)

# insert REMARKS after "1 !NTITLE"
with open('charmm_truncated_atomtypes.psf','r+') as f:
    lines = f.readlines()
    for i,l in enumerate(lines):
        if l.strip() == "1 !NTITLE":
            print("Added REMARKS line")
            lines[i+1] = " REMARKS Parmed-generated NAMD/X-Plor PSF structure file\n"
            break
    f.seek(0)
    f.writelines(lines)
    f.truncate()
