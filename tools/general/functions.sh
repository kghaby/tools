#random functions that are useful in scripts

testfile () {
    echo "#!/bin/bash" > $1
    echo "set -e" >> $1
    chmod a+x $1
    vim $1
}

#function for connecting to remote jupyter-lab
jllocal() {
  rport=27648
  lport=27648
  remote_username=kyleghaby
  remote_hostname=beagle3.rcc.uchicago.edu
  url="http://localhost:$lport"
  echo "URL: $url"
  #open "$url"
  cmd="ssh -NL localhost:$lport:localhost:$rport $remote_username@$remote_hostname"
  echo "Running '$cmd'"
  eval "$cmd"
}

#compares 2 files
comparetxt() {
    sdiff $1 $2 | more
}

addignore() {
    echo "Adding a .gitignore file to:"
    find . -depth -not -path "*target*" -not -path "./.git/*" -type d -empty -print
    find . -depth -not -path "*target*" -not -path "./.git/*" -type d -empty -exec touch {}/.gitignore \;
}

verify_target() {
    local target=$1
    local whitelist=$2
    local blacklist=$3

    #check whitelist
    if (( "${#whitelist[@]}" > 0 )); then
        for item in "${whitelist[@]}"; do
            if [[ "$target" != *"$item"* ]]; then
                return 1
            fi
        done
    fi

    #check blacklist
    if (( "${#blacklist[@]}" > 0 )); then
        for item in "${blacklist[@]}"; do
            if [[ "$target" == *"$item"* ]]; then
                return 1
            fi
        done
    fi
    return 0
}

# Function to create a label from a directory path
label_target() {
    local target_path=$1
    local dirs=$2
    IFS='/' read -ra target_parts <<< "$target_path"
    IFS='/' read -ra dirs_parts <<< "$dirs"
    
    local label_parts=()
    for index in "${!dirs_parts[@]}"; do
        if [[ "${dirs_parts[index]}" == "*" ]]; then
            label_parts+=("${target_parts[index]}")
        fi
    done

    local label=$(IFS=_; echo "${label_parts[*]}")
    echo $label
}


