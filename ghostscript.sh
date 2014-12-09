#!/usr/bin/env sh

# Check if Ghostscript is installed
if [ ! -f /usr/local/bin/gs ]; then
    echo >&2 "Ghostscript is not installed!"
    exit 1     # exit status 0 for success, 1 for failure
fi

# Read user input
#echo "Enter the ID number followed by ENTER:"
#read id_num


files="$directory + /*"

# From stackoverflow - merging pdf files
# gs -dBATCH -dNOPAUSE -q -sDEVICE=pdfwrite -sOutputFile=finished.pdf file*pdf

# Need to reduce size of final pdf.
