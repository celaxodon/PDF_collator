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
if [ ! -f /usr/local/bin/gs ]; then
        echo "Ghostscript is not installed!"
        echo "You can download it here: hppt://pages/uoregon.edu/koch/"
        exit 1
fi

# check for correct volumes mounted
#if [[ -d /Volumes/??? ]]
#fi

#*************#
### ALIASES ###
#*************#

ToPDF='/Users/klurl/Desktop/ASI_Work/Scripts/PDF_collator/Testing/ToPDF/'
export ToPDF # For -exec subshell purposes
ToFile='/Users/klurl/Desktop/ASI_Work/Scripts/PDF_collator/Testing/ToFile/'
ToStrip='/Users/klurl/Desktop/ASI_Work/Scripts/PDF_collator/Testing/Files_to_strip/'
CoC_dir='/Users/klurl/Desktop/ASI_Work/Scripts/PDF_collator/Testing/''!Current COCs''/'

#*******************#
### NAME STRIPPER ###
#*******************#

# Remove "job_", 4 digits and a blank space
# Also put PDF_id loop in this function? Does it matter? Test w/ $ time
name_stripper() {
    for file in *; do
        mv "$file" $(pwd)/"${file#job_[[:digit:]][[:digit:]][[:digit:]][[:digit:]]\ }";
    done
}

clear; 

# Go to the directory for raw pdf files
cd $ToStrip;

name_stripper;

#******************#
### PDF ID ARRAY ###
#******************#

# Array with PDF id nums to compare against CoC dirs
PDF_ids=()
# Note that sed usage here may be unique to OS X. Linux options differ. 
# Also accounting for misspellings of 'pg' with nearby chars. 
for item in *; do
    PDF_ids+=($(echo $item | sed -E 's/[otpg]{2}[0-9]+\.pdf$//g'));
done                                          

echo "File names stripped.";
echo;

### FIX ME ###
# Eventually need to account for non-conforming PDFs in this folder before mv.
mv * $ToPDF;

# May be optional. Could just keep them in the same folder, create temps
# and collate.
echo "Moved PDFs to 'ToPDF' folder.";
echo;

#*****************#
### COC GRABBER ###
#*****************#


# Change to 'mv' if we can just take the CoCs out.
find_coc() {
    for id in ${PDF_ids[@]}; do
        find "$CoC_dir" -name "$id"*.pdf -exec sh -c 'cp "$@" "$ToPDF"' X '{}' +
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

collect_reports() {
    # Generate range to grab pdfs + chain
    for chain in *coc*; do
       if [[ ${#chain} > 18 ]] # Catch range cocs
           then                   
               first=$(echo ${chain:0:3}$(echo $chain | sed -E 's/.*-//' \
                       | sed -E 's/[a-d]?coc.pdf$//'));
               last=$(echo $chain | sed -E 's/[a-d]?[optg]{2}7.*\.pdf$//');
               range=$(seq $first $last);
               mkdir "$last"_tmp;
               # move pdfs to appropriate folder
               for num in $range; do
                       mv $num*.pdf "$last"_tmp;
               done
       else  # a single id coc - accounts for "a-d" files. Cut them out. 
               range=$(echo "$chain" | sed -E 's/[a-d]?[optg]{2}7coc.pdf$//'); 
               mkdir "$range"_tmp;
               mv "$range"*.pdf ./"$range"_tmp/;
       fi
   done
       
}

cd $ToPDF
echo "Collecting reports...";
echo;

collect_reports;


#***************************#
### GHOSTSCRIPT COLLATION ###
#***************************#

tmp_size=0
filename="Report"

collate_pdfs() {
        for dir in ./*; do
            cd "$ToPDF"$dir;
            ls
            # Run ghostscript. CANNOT use line breaks (\)
            gs -dBATCH -dNOPAUSE -q -sDEVICE=pdfwrite -dAutoRotatePages=/PageByPage -sOutputFile="$filename.pdf" ./*.pdf
            # Get file counts in target dir for renaming purposes. Want +1 extra
            # for renaming purposes.
            file_nums=$(ls -l $ToFile | wc -l | sed -E 's/^[ \w\t]*//')
            if [[ "$file_nums" = 0 ]]
                then 
                    mv "$filename".pdf $ToFile"$filename"_1.pdf;
                else
                    mv "$filename".pdf $ToFile"$filename"_"$file_nums".pdf;
            fi
            # Return to $ToPDF folder
            cd ..;
        done
}

collate_pdfs && echo "Report collated. Ready for renaming in $ToFile."

exit 0
