#!/usr/bin/env bash

#********************######################**************#
#                  PDF Collator Script                   #
#                Written by Graham Leva                  #
#            Copyright (c) 2014 Analysys, Inc.           #
#       A script to strip "job_#### " from filenames,    #
#    find matching CoCs, and catenate pdfs into one PDF  #
#**********************************#######################

# Consider 'unset CDPATH' if you want relative directories!

#***********************#
### DEPENDENCY CHECKS ###
#***********************#

# Check for gs installed
if [[ ! -f /usr/local/bin/gs ]]; then
        echo "Ghostscript is not installed!"
        echo "You can download it here: http://pages.uoregon.edu/koch/"
        exit 1
fi

# check for correct volumes mounted
if [[ ! -d /Volumes/scans/ ]]; then
        echo 'Error! Volume "scans" has not been mounted. Please connect to and mount before running this script again.'
        exit 1
fi

if [[ ! -d /Volumes/Data/ ]]; then
        echo 'Error! Volume "Data" has not been mounted. Please connect to and mount before running this script again.'
        exit 1
fi

#*************#
### ALIASES ###
#*************#

# Test directories
#ToPDF=''
#ToFile=''
#ToStrip=''
#CoC_dir=''

# Active directories
ToPDF=''
ToFile=''
ToStrip=''
CoC_dir=''

export ToPDF # For -exec subshell purposes

# Check that necessary folders are available:
if [[ ! -d "$ToPDF" ]]; then
        echo "Folder "$ToPDF" is not accessible. Needs correction in code."
        exit 1
fi

if [[ ! -d "$ToFile" ]]; then
        echo "Folder "$ToFile" is not accessible. Needs correction in code."
        exit 1
fi

if [[ ! -d "$ToStrip" ]]; then
        echo "Folder "$ToStrip" is not accessible. Needs correction in code."
        exit 1
fi

if [[ ! -d "$CoC_dir" ]]; then
        echo "Folder "$CoC_dir" is not accessible. Needs correction in code."
        exit 1
fi


#***********#
### USAGE ###
#***********#

usage() {
    clear;
    cat <<END
    usage: PDF_collator.sh [-c] [-help]

DESCRIPTION:
    This script pulls PDFs and their matching Chain of Custodies (CoCs) from 
    their respective directories and collates them into a report. 

    -c
        Clean option. Will clean out the temporary directory. Returns PDF files
        and CoCs to their source locations and removes temporary directories.

    -help 
        Display this help documentation.

END

exit 0
}

#*******************#
### NAME STRIPPER ###
#*******************#

# Remove "job_", some number of digits and a blank space
name_stripper() {
    # Test if there are files to grab
    if [[ $(ls | wc -l | sed -E 's/^ *//g') = 0 ]]
        then 
            echo "No files found for collation. Exiting program."
            exit 1
    fi

    for file in *; do
        newname=$(echo "$file" | sed -E 's/^'job_'[[:digit:]]*.//')
        mv "$file" "$newname"
    done
}


#*****************#
### COC GRABBER ###
#*****************#
# Finds CoCs that match PDF numbers (in $PDF_ids array)

# Change to 'mv' if we can just take the CoCs out.
find_coc() {
    for id in ${PDF_ids[@]}; do
        find "$CoC_dir"/'1. Corpus' -name "$id"*.pdf -exec sh -c 'cp "$@" "$ToPDF"; mv "$@" ~/.Trash' X '{}' +
        find "$CoC_dir"/'2. Austin' -name "$id"*.pdf -exec sh -c 'cp "$@" "$ToPDF"; mv "$@" ~/.Trash' X '{}' +
    done
}


#*********************#
### COLLECT REPORTS ###
#*********************#
# Collects related PDFs and CoCs, creates a temp dir with last number in range.

range=()
first=""
last=""

# Standard coc filename length = 13 --> 123456coc.pdf
# Multi-ID coc filename length = 17 --> 123450-456coc.pdf
# Single rerun coc filename length = 14 --> 123456acoc.pdf
# Multi-ID rerun coc filename lenght = 19 --> 123450a-456acoc.pdf
# QC/WP/SP samples have NO RANGES, but take the form QCXXX-XXXcoc.pdf (16)

collect_reports() {
    for chain in *c?c.pdf; do         
        if [[ ${#chain} > 16 ]]; then   # range CoCs
               first=$(echo ${chain:0:6});
               last=$(echo ${chain:0:3}$(echo $chain | sed -E 's/.*-//' \
                       | sed -E 's/[a-d]?c.c\.pdf$//'));

               # catch 1000s place rollover
               if [[ "$first" > "$last" ]]; then      
                       # if 555990-001coc.pdf, then last=555001, so add 1000
                       last=$((last+1000));
               fi

               range=$(seq $first $last);
               mkdir "$last"_tmp;

               # move pdfs to appropriate folder
               for num in $range; do
                       # Make sure all range pdfs exist
                       if test -n "$(shopt -s nullglob; echo "$num"*.pdf)"; then 
                           mv "$num"*.pdf "$last"_tmp;
                       else
                           echo "                          WARNING!   ";
                           echo;
                           echo "CoC $(echo "$last"*c?c*.pdf) indicates ranges of files which do not exist in "$ToStrip"";
                           echo "Please return CoC to where it came from.";
                           echo;
                       fi
               done
       # Handle QC/WP/SP files; match regex
       elif [[ ${chain:0:2} =~ ('QC'|'SP'|'WP') ]]; then 
           qc=$(echo $chain | sed -E 's/c.c\.pdf$//');
           # Consider mktemp -dt "$qc" in next rewrite
           mkdir "$qc"_tmp;
           mv "$qc"*.pdf ./"$qc"_tmp/;
       else  # a single id coc - accounts for "a-d" files. Cut them out. 
           val=$(echo "$chain" | sed -E 's/[a-d]?c.c\.pdf$//'); 
           mkdir "$val"_tmp;
           mv "$val"*.pdf ./"$val"_tmp/;
       fi
   done
}


#***************************#
### GHOSTSCRIPT COLLATION ###
#***************************#

FILENAME=""

collate_pdfs() {
        # Check and remove extraneous PDFs that did not match any CoCs
        # This runs no matter what...
        if test -n "$(find . -maxdepth 1 -name "*.pdf" -print -quit)"
            then
                echo "                       WARNING!              ";
                echo "PDF files present that did not match with CoCs!";
                echo "Unmatched PDF files are:";
                echo *.pdf;
                echo;
                echo "Returning unmatched files to original folder.";
                mv "$ToPDF"*.pdf "$ToStrip";
            else
                echo;
                echo "All PDFs in folder matched with chains.";
        fi    

        for dir in ./*; do
            # Move to subdirectory
            cd "$ToPDF"$dir;

            # Get report name from COC in the directory
            FILENAME=$(echo *coc.pdf | sed -E 's/coc//');

            # Reorder files so CoC is last
            for chain in *coc.pdf; do
                    newname=$(echo "last""$chain");
                    mv "$chain" ./"$newname";
            done

            # Run ghostscript. CANNOT use line breaks (\)
            gs -dBATCH -dNOPAUSE -q -sDEVICE=pdfwrite -dAutoRotatePages=/PageByPage -sOutputFile="$FILENAME" ./*.pdf 2>/dev/null;
#            if [[ $? != 0 ]]; then
#                    echo "Ghostscript failed to collate PDFs. Cleanup needed."
#                    exit 1
#            fi

            mv -i "$FILENAME" "$ToFile""$FILENAME";

            # Return to $ToPDF folder
            cd ..;
        done
}


# Remove tmp dirs in hidden folder
clean_up() {  
    cd "$ToPDF";
    echo;
    echo "Cleaning up temporary files...";
    echo;
    echo "Moving collated PDFs and used CoCs to the trash.";
    find "$ToPDF" -name *.pdf -exec sh -c 'mv "$@" ~/.Trash' X '{}' +
    rmdir ./*;
    echo;
}            


main() {

    clear; 

    # Go to the directory for raw pdf files
    cd "$ToStrip";

    name_stripper;

    echo "File names stripped.";
    echo;

    # Create PDF ID array #

    # Array with PDF id nums to compare against CoC dirs
    PDF_ids=()

    # Consider mktemp here

    # Note that sed usage here may be unique to OS X. Linux options differ. 
    # Also accounting for misspellings of 'pg' with nearby chars. 
    for item in *; do
        echo "$item" | sed -E 's/[otpg]{2}[0-9]+\.pdf$//g' >> temp;
    done                                          

    # Create unique  list of PDF IDs from temp file
    PDF_ids=($(sort -u < temp));
    rm temp;
    mv * "$ToPDF";

    # Move all PDFs to 'ToPDF' folder
    echo "Moved PDFs to 'ToPDF' folder.";
    echo;

    echo "Populating with CoCs...";
    echo;

    find_coc;

    cd "$ToPDF"
    echo "Collecting reports...";

    collect_reports;

    echo;

    echo "Collating PDFs...";
    echo;

    collate_pdfs;

    clean_up && echo "Reports collated!";
    echo;
}

main;

exit 0
