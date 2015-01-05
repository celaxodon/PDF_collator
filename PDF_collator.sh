#!/usr/bin/env bash

#********************######################**************#
#                  PDF Collator Script                   #
#                Written by Graham Leva                  #
#              Copyright 2014 Analysys, Inc.             #
#       A script to strip "job_#### " from filenames,    #
#    find matching CoCs, and catenate pdfs into one PDF  #
#**********************************#######################

#Consider 'unset CDPATH' if you want relative directories!

#***********************#
### DEPENDENCY CHECKS ###
#***********************#

# Check for gs installed
if [[ ! -f /usr/local/bin/gs ]]; then
        echo "Ghostscript is not installed!"
        echo "You can download it here: hppt://pages/uoregon.edu/koch/"
        exit 1
fi

# check for correct volumes mounted
if [[ ! -d /Volumes/scans/ ]]; then
        echo 'Error! Volume "scans" has not been mounted. Please connect to and mount before running this script again.'
        exit 1
fi

if [[ ! -d /Volumes/Server/ ]]; then
        echo 'Error! Volume "Server" has not been mounted. Please connect to and mount before running this script again.'
        exit 1
fi

#*************#
### ALIASES ###
#*************#

# NOTE: Need strong quotes for dirs starting with exclamation points (!).
#ToPDF='/Users/imac11/Programming/Scripts/PDF_collator/Testing/.ToPDF/'
ToPDF='/Volumes/Server/!!Data Review/.ToPDF/'
export ToPDF # For -exec subshell purposes
#ToFile='/Users/imac11/Programming/Scripts/PDF_collator/Testing/ToFile/'
ToFile='/Volumes/Server/!!Data Review/8. Completed Reports to File/'
#ToStrip='/Users/imac11/Programming/Scripts/PDF_collator/Testing/Files_to_strip/'
ToStrip='/Volumes/Server/!!Data Review/5. Data Qual Review Complete/'
#CoC_dir='/Users/imac11/Programming/Scripts/PDF_collator/Testing/''!Current COC''/'
CoC_dir='/Volumes/scans/!Current COC/' 

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


#*******************#
### NAME STRIPPER ###
#*******************#

# Remove "job_", some number of digits and a blank space
name_stripper() {
    for file in *; do
        newname=$(echo "$file" | sed -E 's/^'job_'[[:digit:]]*.//')
        mv "$file" "$newname"
    done
}

clear; 

# Go to the directory for raw pdf files
cd "$ToStrip";

# Test if there are files to grab
if [[ $(ls | wc -l | sed -E 's/^ *//g') = 0 ]]
    then 
        echo "No files found for collation. Exiting program."
        exit 1
fi

name_stripper;
echo "File names stripped.";
echo;


#******************#
### PDF ID ARRAY ###
#******************#

# Array with PDF id nums to compare against CoC dirs
PDF_ids=()

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

#*****************#
### COC GRABBER ###
#*****************#


# Change to 'mv' if we can just take the CoCs out.
find_coc() {
    for id in ${PDF_ids[@]}; do
        find "$CoC_dir"/'1. Corpus' -name "$id"*.pdf -exec sh -c 'cp "$@" "$ToPDF"; mv "$@" ~/.Trash' X '{}' +
        find "$CoC_dir"/'2. Austin' -name "$id"*.pdf -exec sh -c 'cp "$@" "$ToPDF"; mv "$@" ~/.Trash' X '{}' +

    done
}

echo "Populating with CoCs...";
echo;
find_coc;

#*********************#
### COLLECT REPORTS ###
#*********************#


range=()
first=""
last=""

# Standard coc filename length = 16 --> 123456pg7coc.pdf
# Multi-ID coc filename length = 20 --> 123456pg7-450coc.pdf
# Single rerun coc filename length = 17 --> 123456apg7coc.pdf
# Multi-ID rerun coc filename lenght = 22 --> 123456apg7-450acoc.pdf
# QC/WP/SP samples have NO RANGES.
# Note that you could use =~ for matching extended regexes

collect_reports() {
    # Generate range to grab pdfs + chain
    for chain in *c?c*; do
       # Catch range cocs
       if [[ ${#chain} > 19 ]]; then
               first=$(echo ${chain:0:3}$(echo $chain | sed -E 's/.*-//' \
                       | sed -E 's/[a-d]?c.c\.pdf$//'));
               last=$(echo $chain | sed -E 's/[a-d]?[optg]{2}7.*\.pdf$//');
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
       # Handle QC/WP/SP files
       elif [[ ${chain:0:2} =~ ('QC'|'SP'|'WP') ]]; then 
           qc=$(echo $chain | sed -E 's/[pgot]{2}7c.c\.pdf$//');
           mkdir "$qc"_tmp;
           mv "$qc"*.pdf ./"$qc"_tmp/;
       else  # a single id coc - accounts for "a-d" files. Cut them out. 
           val=$(echo "$chain" | sed -E 's/[a-d]?[optg]{2}7c.c\.pdf$//'); 
           mkdir "$val"_tmp;
           mv "$val"*.pdf ./"$val"_tmp/;
       fi
   done
}

cd "$ToPDF"
echo "Collecting reports...";
echo;

collect_reports;
echo;

#***************************#
### GHOSTSCRIPT COLLATION ###
#***************************#

#tmp_size=0
filename="Report"

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
                echo;
            else
                echo "All PDFs in folder matched with chains."
        fi    

        for dir in ./*; do
            cd "$ToPDF"$dir;
            # Run ghostscript. CANNOT use line breaks (\)
            gs -dBATCH -dNOPAUSE -q -sDEVICE=pdfwrite -dAutoRotatePages=/PageByPage -sOutputFile="$filename.pdf" ./*.pdf 2>/dev/null;
#            if [[ $? != 0 ]]
#                then
#                    echo "Ghostscript failed to collate PDFs. Cleanup needed."
#                    exit 1
            # Get file counts in target dir for renaming purposes. Want +1 extra
            # for renaming purposes.
            file_nums=$(ls -l "$ToFile" | wc -l | sed -E 's/^[ \w\t]*//')
            if [[ "$file_nums" = 0 ]]
                then 
                    mv "$filename".pdf "$ToFile""$filename"_1.pdf;
                else
                    mv "$filename".pdf "$ToFile""$filename"_"$file_nums".pdf;
            fi
            # Return to $ToPDF folder
            cd ..;
        done
}

echo "Collating PDFs...";
echo;
collate_pdfs;

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

clean_up && echo "Reports collated!";
echo;

exit 0
