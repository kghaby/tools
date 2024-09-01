#!/bin/bash
#random functions that are useful in scripts


linker () {
    mkdir .lsp_symlink
    cd .lsp_symlink
    ln -s "$1" "$2"
}

testfile () {
    echo "#!/bin/bash" > "$1"
    echo "set -e" >> "$1"
    chmod a+x "$1"
    vim "$1"
}

#function for connecting to remote jupyter-lab
jllocal() {
  rport=27648
  lport=27648
  remote_username="$1" #eg kyleghaby
  remote_hostname="$2" #eg beagle3.rcc.uchicago.edu
  url="http://localhost:$lport"
  echo "URL: $url"
  #open "$url"
  cmd="ssh -NL localhost:$lport:localhost:$rport $remote_username@$remote_hostname"
  echo "Running '$cmd'"
  eval "$cmd"
}

#compares 2 files
comparetxt() {
    sdiff "$1" "$2" | more
}

addignore() {
    echo "Adding a .gitignore file to:"
    find . -depth -not -path "*target*" -not -path "./.git/*" -type d -empty -print
    find . -depth -not -path "*target*" -not -path "./.git/*" -type d -empty -exec touch {}/.gitignore \;
}
verify_target() {
    local target="$1"

    # check whitelist
    if (( ${#whitelist[@]} > 0 )); then
        local found=0
        for item in "${whitelist[@]}"; do
            if [[ "$target" == *"$item"* ]]; then
                found=1
                break
            fi
        done
        if (( found == 0 )); then
            return 1
        fi
    fi

    # check blacklist
    if (( ${#blacklist[@]} > 0 )); then
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
    local target_path="$1"
    local targets="$2"
    IFS='/' read -ra target_parts <<< "$target_path"
    IFS='/' read -ra targets_parts <<< "$targets"

    local label_parts=()
    for index in "${!targets_parts[@]}"; do
        if [[ "${targets_parts[index]}" == "*" ]]; then
            label_parts+=("${target_parts[index]}")
        fi
    done

    local label=$(IFS=_; echo "${label_parts[*]}")
    echo "$label"
}

extract_mic_track() {
    # Usage:
    # extract_mic_track "Desktop 2024.09.01 - 18.05.00.17.DVR.mp4"
    if [ $# -eq 0 ]; then
        echo "No filename provided."
        return 1
    fi

    local input_file="$1"
    local output_file="${input_file%.*}_mic.aac"

    if ! [ -f "$input_file" ]; then
        echo "File does not exist: $input_file"
        return 1
    fi

    ffmpeg -i "$input_file" -map 0:a:1 -c:a copy "$output_file" 2>/dev/null
    if [ $? -eq 0 ]; then
        echo "Extracted mic track successfully: $output_file"
    else
        echo "Failed to extract mic track."
        return 1
    fi
}


