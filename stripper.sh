#!/usr/bin/env sh

# Strip out file names from pwd

#####################
### NAME STRIPPER ###
#####################

clear;

# Go to the directory for raw pdf files
DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd );
echo "Running in "$DIR"";

# Remove "job_", 4 digits and a blank space
# Also put PDF_id loop in this function? Does it matter? Test w/ $ time
name_stripper() {
    for file in $DIR/*; do
        mv "$file" "${file#job_[[:digit:]][[:digit:]][[:digit:]][[:digit:]]\ }";
done
}

#name_stripper;

echo "File names stripped.";

sleep 10;

#exit 0
