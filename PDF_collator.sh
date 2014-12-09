#!/usr/bin/env bash

# A script to catenate pdfs, possibly turn them and combine with CoCs

# First, strip leading "job_" chars

# Go to the appropriate directory for raw pdf files
cd ~/Programming/Scripts/PDF_collator/Testing/Files_to_strip/;

# Remove "job_", 4 digits and a blank space
name_stripper() {
    for file in *; do
            mv "$file" $(pwd)/"${file#job_[[:digit:]][[:digit:]][[:digit:]][[:digit:]]\ }";
    done
}

# Run the function
name_stripper;


# consider adding the sample id to an array to help search for coc
find_coc() {

# Search 3 paths: (1) pwd; (2) '!! Austin'; (3) !! 'Corpus'
}
exit 0
