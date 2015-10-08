#!/bin/bash

# A script to check for improperly named files in CoC folders.

# This script is run via cron each day at 3:15PM. The following is the cronjob:
# 3 13 * * 1-5 /usr/local/bin/name_check.sh > /var/log/name_check/name_check.log;
# if [[ $? -eq 1 ]]; then mailx -s "CoC errors found" gleva@analysysinc.com,..., < /var/log/name_check/name_check.log; else exit 0; fi

#*************************#
### DIRECTORY LOCATIONS ###
#*************************#

Corpus_CoCs='/Volumes/OSX Server/scans/!Current COC/1. Corpus/'
#Corpus_CoCs='/Users/imac11/Programming/Scripts/PDF_collator/Testing/!Current COC/1. Corpus/'
Austin_CoCs='/Volumes/OSX Server/scans/!Current COC/2. Austin/'
#Austin_CoCs='/Users/imac11/Programming/Scripts/PDF_collator/Testing/!Current COC/2. Austin/'

bad_files=();

# Cannot seem to get bad_files+=(<expr>) to work!
check() {
    cd "$Corpus_CoCs"
    for file in *; do
            echo "$file" | egrep -v -e '[[:digit:]]{6}[a-d]?(-[[:digit:]]{3}[a-d]?)?coc\.pdf' -e '(QC|WP|SP)[[:digit:]]{3}-[[:digit:]]{3}coc\.pdf' 1>/dev/null;
        if [[ $? = 0 ]]; then
            bad_files+=($file);
        fi
    done

    cd "$Austin_CoCs"

    for file in *; do
            echo "$file" | egrep -v -e '[[:digit:]]{6}[a-d]?(-[[:digit:]]{3}[a-d]?)?coc\.pdf' -e '(QC|WP|SP)[[:digit:]]{3}-[[:digit:]]{3}coc\.pdf' 1>/dev/null;
        if [[ $? = 0 ]]; then
            bad_files+=($file);
        fi
    done

    if [[ ${#bad_files[@]} != 0 ]]; then
        echo "         *** WARNING! ***";
        echo;
        echo "There appear to be mistyped filenames: ";
        echo;
        echo "+-----------------------------------+";
        for i in ${bad_files[@]}; do
            printf "\t%s\t\n" "$i";
        done
        date "+DATE: %Y-%m-%d%nTIME: %H:%M:%S";
        echo "+-----------------------------------+";
        exit 1     # Bad files were found. Exit with failure status
    fi
}

check;

exit 0
