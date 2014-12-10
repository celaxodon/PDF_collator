#!/usr/bin/env sh

# Check if Ghostscript is installed
if [ ! -f /usr/local/bin/gs ]; then
    echo "Ghostscript is not installed!" 
    echo "You can download here: http://pages.uoregon.edu/koch/"
    exit 1     # exit status 0 =  success, 1 = failure
fi

# Take arg1 (directory) and perform the collation
cd $1

#files="$directory + /*"
datestamp="$(date "+%m-%d-%y")"

# Define file name for output
name="example $datestamp" 

# From stackoverflow - merging pdf files
gs -dBATCH -dNOPAUSE -q -sDEVICE=pdfwrite -dAutoRotatePages=/PageByPage -sOutputFile=${name}.pdf ./*.pdf

# Syntax for I/O redirection (doesn't work with lists of pdfs!
#gs -dBATCH -dNOPAUSE -q -sDEVICE=pdfwrite -dAutoRotatePages=/PageByPage -sOutputFile=out.pdf -_ < file_list.txt

# note that the option -dPDFSETTINGS=/prepress will only compress things above 300 dpi
