#!/usr/bin/env sh 
# Check if Ghostscript is installed
if [ ! -f /usr/local/bin/gs ]; then
    echo "Ghostscript is not installed!" 
    echo "You can download here: http://pages.uoregon.edu/koch/"
    exit 1     # exit status 0 =  success, 1 = failure
fi

# Take arg1 (directory) and perform the collation
cd $1

tmp_size=0
get_orig_size() {
    for file in *; do
        tmp_size=$(($tmp_size + $(du -h $file | sed -E 's/K.*//g')));
    done
}

#datestamp="$(date "+%m-%d-%y")"

# Define file name for output. Would be great to be able to pull out name from
# field in file. Possibly with python PyPDF2.
name="example" 

# Merge pdf files, output with above name.
gs -dBATCH -dNOPAUSE -q -sDEVICE=pdfwrite -dAutoRotatePages=/PageByPage -sOutputFile=${name}.pdf ./*.pdf

#comp_size=$(du -h )
# Syntax for I/O redirection (doesn't work with lists of pdfs!
#gs -dBATCH -dNOPAUSE -q -sDEVICE=pdfwrite -dAutoRotatePages=/PageByPage -sOutputFile=out.pdf -_ < file_list.txt

# note that the option -dPDFSETTINGS=/prepress will only compress things above 300 dpi
