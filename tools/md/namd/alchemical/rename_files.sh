#!/bin/bash
shopt -s extglob

BFEE_dir="BFEE"

dirs=(001_MoleculeBound 002_RestraintBound 003_MoleculeUnbound 004_RestraintUnbound)
for d in "${dirs[@]}"; do
  echo ""
  echo "File matches in $d"
  # rename files: _backward.* -> _backward1.*, _forward.* -> _forward1.*
  find "${BFEE_dir}/$d" -type f | while IFS= read -r f; do
    base=${f##*/}
    #echo $f $base
    if [[ $base == *@(fep|ti)_backward.* ]]; then
      prefix=${base%%_backward\.*}
      suffix=${base#*_backward\.}
      new="${prefix}_backward1.${suffix}"
    elif [[ $base == *@(fep|ti)_forward.* ]]; then
      prefix=${base%%_forward\.*}
      suffix=${base#*_forward\.}
      new="${prefix}_forward1.${suffix}"
    else
      continue
    fi
    dst="$(dirname "$f")/$new"
    echo "mv '$f' '$dst'"
    mv "$f" "$dst"
  done

  # rename in-file instances
  echo ""
  echo "In-file matches in $d:"
  echo "  For non-output"
  # check 
  find "${BFEE_dir}/$d" -type f \( -name '*.conf' -o -name '*.slurm' \) -print0 \
      | xargs -0 grep -Hn -E '(fep|ti)_backward\.|(fep|ti)_forward\.'
  # do
  find "${BFEE_dir}/$d" -type f \( -name '*.conf' -o -name '*.slurm' \) -print0 | xargs -0 -I{} bash -c "
    echo 'sed in {}'
    sed -i -E \\
      -e 's#(fep|ti)_backward\.#\1_backward1.#g' \\
      -e 's#(fep|ti)_forward\.#\1_forward1.#g' \\
    {}"


  echo "  For output"
  # check
  find "${BFEE_dir}/$d" -type f \( -name '*1.conf' -o -name '*1.slurm' \) -print0 \
      | xargs -0 grep -Hn -E 'output/[[:alnum:]]+_backward[[:space:]]+|output/[[:alnum:]]+_forward[[:space:]]+'
  # do
  find "${BFEE_dir}/$d" -type f \( -name '*1.conf' -o -name '*1.slurm' \) -print0 | xargs -0 -I{} bash -c "
    echo 'sed in {}'
    sed -i -E \\
      -e 's#(output/[[:alnum:]]+)_backward([[:space:]]+)#\1_backward1\2#g' \\
      -e 's#(output/[[:alnum:]]+)_forward([[:space:]]+)#\1_forward1\2#g' \\
    {}"

  echo ""
done


