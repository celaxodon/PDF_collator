#!/usr/bin/env sh

# Check if Ghostscript is installed
if [ ! -f /usr/local/bin/gs ]; then
    echo "Ghostscript is not installed! Download here: http://pages.uoregon.edu/koch/"
    exit 1     # exit status 0 for success, 1 for failure
fi

# Change to directory where PDF_collator.sh is running
cd $1

name="example"  # Output file name
# Notes that 'ls -1U | wc -l' returns the number of files in a directory

# From stackoverflow - merging pdf files
gs -dBATCH -dNOPAUSE -q -sDEVICE=pdfwrite -dAutoRotatePages=/PageByPage -sOutputFile=${name}.pdf ./*.pdf

# Syntax for I/O redirection (doesn't work with lists of pdfs!
#gs -dBATCH -dNOPAUSE -q -sDEVICE=pdfwrite -dAutoRotatePages=/PageByPage -sOutputFile=out.pdf -_ < file_list.txt

# note that the option -dPDFSETTINGS=/prepress will only compress things above 300 dpi
