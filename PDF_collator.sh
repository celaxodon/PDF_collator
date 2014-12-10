#!/usr/bin/env bash

# A script to strip "job_#### " from filenames, find matching CoCs,
# and catenate pdfs into one PDF.

###########################
###      ALIASES        ###
###########################

ToPDF='/Users/imac11/Programming/Scripts/PDF_collator/Testing/ToPDF/'
# Check me!
#ToFile='/Users/imac11/Programming/Scripts/PDF_collator/Testing/???'
ToStrip='/Users/imac11/Programming/Scripts/PDF_collator/Testing/Files_to_strip/'
# Check me!
CoC_dir='/Users/imac11/Programming/Scripts/PDF_collator/Testing/''!Current COCs''/'

###########################

# Go to the appropriate directory for raw pdf files
cd $ToStrip;

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
echo \n;
mv * $ToPDF;    # All files in original directory moved. Fix???
# May just be able to skip this step, create a temp dir and call ghostscript.
echo "Moved PDFs to 'ToPDF' folder.";
#echo "PDF IDs are: ${PDF_ids[@]}";
echo \n;

echo "Populating with CoCs...";
echo \n;

# Not sure whether to take the CoCs out of the folder or not!
find_coc() {
    for id in ${PDF_ids[@]}; do
        find /Users/imac11/Programming/Scripts/PDF_collator/Testing/'!Current COCs'/ -name $id*.pdf -exec cp '{}' $ToPDF
}


# Eventually, call ghostscript script, using $1 as desired directory
#exec ghostscript.sh $(pwd)

# find_coc() && echo "Report collated. Ready for renaming in $ToFile."

exit 0
