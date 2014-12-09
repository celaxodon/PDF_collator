#!/usr/bin/env sh

# Check if Ghostscript is installed
checkdeps() {

    if [ -e /usr/local/bin/gs ]; then
        echo "Ghost script is installed."; 
    else
        echo >&2 "dependency Ghostscript is needed. Please install before coninuing."
    # need to figure out what the right exit status is and how to code it
        exit 1
    fi

}

# Alternatively, check if a file exists with:
if [ ! -f /usr/local/bin/gs ]; then
    echo "Ghostscript is not installed!"
    exit 1     # exit status 0 for success, 1 for failure
fi

files="$directory + /*"

# From stackoverflow - merging pdf files
# gs -dBATCH -dNOPAUSE -q -sDEVICE=pdfwrite -sOutputFile=finished.pdf file*pdf

# Need to reduce size of final pdf.
