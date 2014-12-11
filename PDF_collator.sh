#!/usr/bin/env bash

# A script to strip "job_#### " from filenames, find matching CoCs,
# and catenate pdfs into one PDF.

###########################
###      ALIASES        ###
###########################

ToPDF='/Users/imac11/Programming/Scripts/PDF_collator/Testing/ToPDF/'
export ToPDF # For -exec subshell purposes
#ToFile='/Users/imac11/Programming/Scripts/PDF_collator/Testing/???' #FIX
ToStrip='/Users/imac11/Programming/Scripts/PDF_collator/Testing/Files_to_strip/'
CoC_dir='/Users/imac11/Programming/Scripts/PDF_collator/Testing/''!Current COCs''/'

#####################
### NAME STRIPPER ###
#####################

clear; 

# Go to the appropriate directory for raw pdf files
cd $ToStrip;

# Remove "job_", 4 digits and a blank space
# Also put PDF_id loop in this function? Does it matter? Test w/ $ time
name_stripper() {
    for file in *; do
        mv "$file" $(pwd)/"${file#job_[[:digit:]][[:digit:]][[:digit:]][[:digit:]]\ }";
    done
}

name_stripper;

### PDF ID ARRAY ###
# Array with PDF id nums to compare against CoC dirs
PDF_ids=()
# Note that usage of sed is unique to OS X. Linux options differ. 
# Also accounting for misspellings of 'pg' with nearby chars. 
for item in *; do
    PDF_ids+=($(echo $item | sed -E 's/[otpg]{2}[0-9]+\.pdf$//g'));
done                                          

echo "File names stripped.";
echo;

# Eventually need to account for non-conforming PDFs in this folder before mv.
mv * $ToPDF;

# May just be able to skip this step, create a temp dir and call ghostscript.
echo "Moved PDFs to 'ToPDF' folder.";
#echo "PDF IDs are: ${PDF_ids[@]}";
echo;

###################
### COC GRABBER ###
###################

echo "Populating with CoCs...";
echo;

# Change to 'mv' if we can just take the CoCs out.
find_coc() {
    for id in ${PDF_ids[@]}; do
        find "$CoC_dir" -name "$id"*.pdf -exec sh -c 'cp "$@" "$ToPDF"' X '{}' +
    done
}

find_coc;

#######################
### COLLECT REPORTS ###
#######################

echo "Collecting reports...";
echo;

range=()
first=""
last=""
cd $ToPDF
collect_reports() {
    for chain in *coc*; do
       if [ ${#chain} = 20..21 ]
           then
           else
       fi
       first=$(sed ${i
       range+=($(
       
}
#collect_reports()
# Eventually, call ghostscript script, using $1 as desired directory
#exec ghostscript.sh $(pwd)

# find_coc() && echo "Report collated. Ready for renaming in $ToFile."

exit 0
