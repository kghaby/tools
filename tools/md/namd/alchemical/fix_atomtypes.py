#!/usr/bin/env python3

resname = "4B9"
bad_psf = "charmm_truncated_atomtypes.psf"
good_psf = f"../../../../build/BTK_{resname}_u_badwater.psf"
out_psf = "charmm.psf" 

# build mapping atomname->atomtype
mapping = {}
with open(good_psf) as f:
    for line in f:
        if len(line) >= 48 and line[29:38].strip() == resname:
            atom = line[38:47].strip()
            mapping[atom] = line[47:55].strip()

# replace truncated types in bad_psf
with open(bad_psf) as fin, open(out_psf, "w") as fout:
    for line in fin:
        if len(line) >= 48 and line[29:38].strip() == resname:
            atom = line[38:47].strip()
            if atom in mapping:
                print(f"Replacing {line[47:55].strip()} with {mapping[atom]}")
                fout.write(line[:47] + mapping[atom].ljust(8) + line[55:])
                continue
        fout.write(line)

print(f"Wrote fixed psf to {out_psf}")


# do these manually after verifying correctness 
# ! mv charmm.psf charmm_truncated_atomtypes.psf
# ! mv charmm_fixed.psf charmm.psf
