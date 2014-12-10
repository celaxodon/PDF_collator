#!/usr/bin/env bash

# A script to strip "job_#### " from filenames, find matching CoCs,
# and catenate pdfs into one PDF.

# Strip leading "job_" chars

# Go to the appropriate directory for raw pdf files

# This is a temporary testing dir
cd ~/Programming/Scripts/PDF_collator/Testing/Files_to_strip/;

# Optionally, query a directory that the files are in, use it as
# an argument in name_stripper().


# Remove "job_", 4 digits and a blank space
name_stripper() {
    for file in *; do
        mv "$file" $(pwd)/"${file#job_[[:digit:]][[:digit:]][[:digit:]][[:digit:]]\ }";
    done
}


# Run the function
name_stripper;
echo "File names stripped."

# Array with PDF id nums to compare against CoC dirs
PDF_ids=()
# Note that usage of sed is unique to OS X. Linux options differ
for item in *; do
    PDF_ids+=($(echo $item | sed -E 's/pg[0-9]+\.pdf$//g'));
done                                          

#echo "PDF id list is: ${PDF_ids[@]}"

#find_coc() {

# Search criteria

# Search 3 paths: (1) pwd; (2) '!! Austin'; (3) !! 'Corpus'

#}

# Eventually, call ghostscript script, using $1 as desired directory
#exec ghostscript.sh $(pwd)

exit 0
