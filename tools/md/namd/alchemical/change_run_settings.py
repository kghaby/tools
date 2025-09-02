#!/usr/bin/env python3
"""
____CHANGES TO FILES (before | after)____
001_MoleculeBound/001.1_fep_backward1.conf (dblwindows for 4A9):
runFEP 1.0 0.0 -0.01 500000                   | runFEP 1.0 0.0 -0.005 1000000

001_MoleculeBound/001.2_fep_forward1.conf (dblwindows for 4A9):
runFEP 0.0 1.0 0.01 500000                    | runFEP 0.0 1.0 0.005 1000000

002_RestraintBound/002.1_ti_backward1.conf (dblsim for 4A9):
run    50500000                                           | run    202000000

002_RestraintBound/002.2_ti_forward1.conf (dblsim for 4A9):
run    50500000                                           | run    202000000

002_RestraintBound/colvars_backward.in (dblsim for 4A9) (FOR ALL 7 COLVARS):
    targetNumSteps      500000                                |     targetNumSteps      2000000

002_RestraintBound/colvars_forward.in (dblsim for 4A9) (FOR ALL 7 COLVARS):
    targetNumSteps      500000                                |     targetNumSteps      2000000


003_MoleculeUnbound/003.1_fep_backward1.conf
runFEP 1.0 0.0 -0.005 500000                      | runFEP 1.0 0.0 -0.005 1000000

003_MoleculeUnbound/003.2_fep_forward1.conf
runFEP 0.0 1.0 0.005 500000                   | runFEP 0.0 1.0 0.005 1000000
"""

from __future__ import annotations
import os, io, re, sys

BFEE_dir = "BFEE" # relative to script location

# 001.* runFEP 
_RUNFEP_BW_PATTERN = re.compile(
    r'^(?P<pre>\s*)runFEP\s+1\.0\s+0\.0\s+-0\.01\s+500000(?P<post>\s*(?:#.*)?)$',
    re.MULTILINE)
_RUNFEP_BW_REPL = r'\g<pre>runFEP 1.0 0.0 -0.005 1000000\g<post>'

_RUNFEP_FW_PATTERN = re.compile(
    r'^(?P<pre>\s*)runFEP\s+0\.0\s+1\.0\s+0\.01\s+500000(?P<post>\s*(?:#.*)?)$',
    re.MULTILINE)
_RUNFEP_FW_REPL = r'\g<pre>runFEP 0.0 1.0 0.005 1000000\g<post>'

# 002.* run steps 50500000 -> 202000000
_RUN_TSTEPS_PATTERN = re.compile(
    r'^(?P<pre>\s*)run(?P<sp>\s+)50500000(?P<post>\s*(?:#.*)?)$',
    re.MULTILINE)
_RUN_TSTEPS_REPL = r'\g<pre>run\g<sp>202000000\g<post>'

# 002.* colvars targetNumSteps 500000 -> 2000000
_TNS_PATTERN = re.compile(
    r'^(?P<pre>\s*targetNumSteps)(?P<sp>\s+)500000(?P<post>\s*(?:#.*)?)$',
    re.MULTILINE)
_TNS_REPL = r'\g<pre>\g<sp>2000000\g<post>'

# 003.* runFEP steps 500000 -> 1000000
_RUNFEP_STEPS_PATTERN = re.compile(
    r'^(?P<pre>\s*runFEP\s+(?:[01](?:\.0)?\s+){2}-?0?\.\d+(?:\s+))500000(?P<post>\s*(?:#.*)?)$',
    re.IGNORECASE | re.MULTILINE)
_RUNFEP_STEPS_REPL = r'\g<pre>1000000\g<post>'

def find_files(root: str):
    for dirpath, _, filenames in os.walk(root):
        for fn in filenames:
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

def endswith_parts(path: str, *parts: str) -> bool:
    norm = os.path.normpath(path)
    tail = os.path.join(*parts)
    return norm.endswith(os.path.normpath(tail))

def transform_text(path: str, text: str) -> tuple[str, list[str]]:
    changes: list[str] = []

    # 001_MoleculeBound transforms
    if endswith_parts(path, "001_MoleculeBound", "001.1_fep_backward1.conf"):
        new = _RUNFEP_BW_PATTERN.sub(_RUNFEP_BW_REPL, text)
        if new != text:
            changes.append("runFEP bw: -0.01/500000 -> -0.005/1000000")
        text = new

    if endswith_parts(path, "001_MoleculeBound", "001.2_fep_forward1.conf"):
        new = _RUNFEP_FW_PATTERN.sub(_RUNFEP_FW_REPL, text)
        if new != text:
            changes.append("runFEP fw: +0.01/500000 -> +0.005/1000000")
        text = new

    # 002_RestraintBound transforms
    if endswith_parts(path, "002_RestraintBound", "002.1_ti_backward1.conf") or \
       endswith_parts(path, "002_RestraintBound", "002.2_ti_forward1.conf"):
        new = _RUN_TSTEPS_PATTERN.sub(_RUN_TSTEPS_REPL, text)
        if new != text:
            changes.append("run steps: 50500000 -> 202000000")
        text = new

    if endswith_parts(path, "002_RestraintBound", "colvars_backward.in") or \
       endswith_parts(path, "002_RestraintBound", "colvars_forward.in"):
        new, n = _TNS_PATTERN.subn(_TNS_REPL, text)
        if n > 0:
            changes.append(f"targetNumSteps: 500000 -> 2000000 (n={n})")
        text = new

    # 003_MoleculeUnbound transforms
    if endswith_parts(path, "003_MoleculeUnbound", "003.1_fep_backward1.conf") or \
       endswith_parts(path, "003_MoleculeUnbound", "003.2_fep_forward1.conf"):
        new = _RUNFEP_STEPS_PATTERN.sub(_RUNFEP_STEPS_REPL, text)
        if new != text:
            changes.append("runFEP steps: 500000 -> 1000000")
        text = new

    return text, changes

def process_file(path: str):
    targets = (
        ("001_MoleculeBound", "001.1_fep_backward1.conf"),
        ("001_MoleculeBound", "001.2_fep_forward1.conf"),
        ("002_RestraintBound", "002.1_ti_backward1.conf"),
        ("002_RestraintBound", "002.2_ti_forward1.conf"),
        ("002_RestraintBound", "colvars_backward.in"),
        ("002_RestraintBound", "colvars_forward.in"),
        ("003_MoleculeUnbound", "003.1_fep_backward1.conf"),
        ("003_MoleculeUnbound", "003.2_fep_forward1.conf"),
    )
    if not any(endswith_parts(path, *t) for t in targets):
        return

    print(f"FILE: {path}")
    
    orig = read_text(path)
    upd, changes = transform_text(path, orig)
    if not changes:
        print("\tUnchanged")
        return
    
    if write_text_if_changed(path, orig, upd):
        for c in changes:
            print(f"\t - {c}")

def main():
    root = os.path.abspath(BFEE_dir)
    if not os.path.isdir(root):
        print(f"BFEE_dir does not exist: {root}", file=sys.stderr)
        sys.exit(1)
    for path in find_files(root):
        try:
            process_file(path)
        except Exception as e:
            print(f"ERROR: {path}: {e}", file=sys.stderr)

if __name__ == "__main__":
    main()

