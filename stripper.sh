#!/usr/bin/env sh

# Strip out file names from pwd

# See: https://bosker.wordpress.com/2012/02/12/bash-scripters-beware-of-the-cdpath
unset CDPATH

#####################
### NAME STRIPPER ###
#####################

clear;

# Go to the directory for raw pdf files
DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd );

cd $DIR && echo "just cd'd to DIR var. Running in $(pwd)"

# Remove "job_", 4 digits and a blank space
# Also put PDF_id loop in this function? Does it matter? Test w/ $ time
name_stripper() {
    for file in *; do
            newname=$(echo "$file" | sed -E 's/^'job_'[[:digit:]]*.//')
            mv "$file" "$newname"
done
}

name_stripper && echo "File names stripped.";

exit 0
