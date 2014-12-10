#!/usr/bin/env bash

# A script to catenate pdfs, possibly turn them and combine with CoCs

# First, strip leading "job_" chars

# Go to the appropriate directory for raw pdf files
# This is a temporary testing dir
cd ~/Programming/Scripts/PDF_collator/Testing/Files_to_strip/;

# Optionally, query a directory that the files are in, use it as
# an argument in name_stripper().

# Remove "job_", 4 digits and a blank space
name_stripper() {
    for file in *; do
            mv "$file" $(pwd)/"${file#job_[[:digit:]][[:digit:]][[:digit:]][[:digit:]]\ }";
            echo "filename is $file"
    done
}

# Array where PDF ids are stored to query against CoC dir
PDF_ids={}

gen_PDF_ids() {
    for file in *; do
        echo ${file%.pdf} > PDF_ids{};
    done
}

# Run the functions
name_stripper;
gen_PDF_ids;

echo "PDF id list is: $PDF_ids"

find_coc() {

# Search criteria

# Search 3 paths: (1) pwd; (2) '!! Austin'; (3) !! 'Corpus'

}
exit 0
