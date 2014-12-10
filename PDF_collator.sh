#!/usr/bin/env bash

# A script to strip "job_#### " from filenames, find matching CoCs,
# and catenate pdfs into one PDF.

###########################
###      ALIASES        ###
###########################

ToPDF='/Users/imac11/Programming/Scripts/PDF_collator/Testing/ToPDF/'

# Go to the appropriate directory for raw pdf files
# This is a temporary testing dir
cd ~/Programming/Scripts/PDF_collator/Testing/Files_to_strip/;

# Optionally, query a directory that the files are in, use it as
# an argument in name_stripper().


# Remove "job_", 4 digits and a blank space
# Also put PDF_id loop in this function? Does it matter? Test w/ $ time
name_stripper() {
    for file in *; do
        mv "$file" $(pwd)/"${file#job_[[:digit:]][[:digit:]][[:digit:]][[:digit:]]\ }";
    done
}

# Run the function
name_stripper;

# Array with PDF id nums to compare against CoC dirs
PDF_ids=()
# Note that usage of sed is unique to OS X. Linux options differ. 
# Also accounting for misspellings of 'pg' with nearby chars. 
for item in *; do
    PDF_ids+=($(echo $item | sed -E 's/[otpg]{2}[0-9]+\.pdf$//g'));
done                                          

echo "File names stripped.";
mv * $ToPDF;
echo "Moved PDFs to 'ToPDF' folder.";
#echo "PDF IDs are: ${PDF_ids[@]}";

echo "Populating with CoCs...";
echo \n;
# Not sure whether to take the CoCs out of the folder or not!
#find_coc() {
#    for id in ${PDF_ids[@]}; do
#        find /Users/imac11/Programming/Scripts/PDF_collator/Testing/'!Current COCs'/ -name $id*.pdf -exec cp '{}' $ToPDF
#}

# Search 3 paths: (1) pwd; (2) '!! Austin'; (3) !! 'Corpus'

#}
# Come back with response message based on PID of find_coc().
# find_coc() && echo 
# Eventually, call ghostscript script, using $1 as desired directory
#exec ghostscript.sh $(pwd)

exit 0
