#!/usr/bin/env sh

# Check if Ghostscript is installed

# Alternatively, check if a file exists with:
if [ ! -f /usr/local/bin/gs ]; then
    echo >&2 "Ghostscript is not installed!"
    exit 1     # exit status 0 for success, 1 for failure
fi


files="$directory + /*"

# From stackoverflow - merging pdf files
gs -dBATCH -dNOPAUSE -q -sDEVICE=pdfwrite -sOutputFile=finished.pdf file*pdf

