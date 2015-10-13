#!/usr/bin/env python3

#---------------------------------------#
#           PDF Collator v.01           #
#        Written by Graham Leva         #
#     Copyright (c) 2015 AnalySys, Inc. #
# Something about the proper license    #
#---------------------------------------#

import sys
import os
import os.path
import logging
import re
import argparse

# For color output
#import colorama

# Location for finished, collated reports
FIN_REPORTS = ''
# Location for reports that have been reviewed, but not collated
REVD_REPORTS = ''
# Location of CoCs
AUS_COCS = ''
CORP_COCS = ''
# Folder to copy reports into after collation
BILLINGS = ''


def system_checks():
    """Check required software is installed and that remote file system
    directories are mounted.
    """
    dir_list = ['Data', 'scans', 'Admin']

    # Check operating system
    if os.uname().sysname != 'Darwin':
        print("Warning! This program was only designed to run on Mac OS X")
        ans = input("Run at your own risk. Continue? (y/n)\n")
        while True:
            lower_ans = str(ans).lower()
            if lower_ans == 'y' or lower_ans == 'yes':
                # Continue with checks
                break
            elif lower_ans == 'n' or lower_ans == 'no':
                return False
            else:
                print("Yes ('y') or no ('n'), please.")
                ans = input("Continue program? (y/n)\n")

    # Check correct volumes from file server mounted
    for d in dir_list:
        if os.path.exists(d): # Directory is mounted
            continue
        else:
            print("This program cannot run unless you have the '{0}' folder "
                  "mounted.".format(d))
            print("Please connect to the file server ('New Server') and run this"
                  " program again.\n")
            return False

    # Test specific directories exist
    for folder in [FIN_REPORTS, REVD_REPORTS, AUS_COCS, CORP_COCS, BILLINGS]:
        if os.path.exists(folder):
            continue
        else:
            print("The folder {0} is not accessible. Please make sure you can"
                  " navigate to the folder before running this"
                  " program again.\n".format(folder))
            return False


def file_check(directory):
    """Test existance of files for collation in target directory."""
    # Consider checking for .afp_[\d]+ files in collation directory

    if len(os.listdir(directory)) == 0:
        return False
    elif len(os.listdir(directory)) == 1 and '.DS_Store' in os.listdir(directory):
        return False
    else:
        return True    # Files exist and they're not irrelevant


def name_check(*args):
    """Test for incorrect Chain of Custody labels before running each time.

    Returns a list of bad file names, or None, if name check passes.
    """

    bad_names = []
    # Need to account for repeat files - 400-400coc.pdf
    # What if two reports needing the same file. Different function - find_cocs
    # Need to account for report ranges decrementing instead of incrementing.
    coc_RE = re.compile('([\\d]{3}([\\d]{3})([a-d]{1})?(-([\\d]{3})(\\3)?)?coc\\.pdf$|(QC|WP|SP)([\\d]{3})-([\\d]{3})coc\\.pdf$)')

    for path in args:
        coc_list = os.listdir(path)
        # Less clear than below
        #clean_list = list(filter(lambda x: x != '.DS_Store', coc_list))
        # Remove OS X-specific directory services store file
        if '.DS_Store' in coc_list:     
            coc_list.remove('.DS_Store')

        for i in coc_list:
            # Check against regex for non-conforming file names 
            match = coc_RE.fullmatch(i)
            # Full match exists!
            if match is not None:
                if i.startswith(("QC", "SP", "WP")):
                    # Don't worry about numbers for these samples.
                    continue
                elif '-' in i:
                    first = int(match.group(2))
                    last = int(match.group(5))
                    diff = abs(last - first)
                    # First range number shouldn't match the second
                    if diff == 0:
                        bad_names.append(i)
                    # Check that second group is incrementing
                    # If range is 400990-010, (incrementing) diff = 980
                    # If range is 400990-960, (decrementing) diff = 30
                    elif last < first and diff < 100:
                        bad_names.append(i)
                    else:
                        continue
                else:
                    # Normal CoCs - 123456coc.pdf or 123456acoc.pdf
                    continue
            else:
                bad_names.append(i)

    if len(bad_names) == 0:
        return None
    else:
        return bad_names
                

def parser_setup():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Rename scanned reports, find'
            ' Chain of Custodies (CoCs) and collate PDF reports.')
    # -h, --help is setup by default
    parser.add_argument('-c', '--clean', help='Clean up temporary directories '
                        'and reset files to starting positions.',
                        action="store_true")
    args = parser.parse_args()
    if args.clean:
        # do something
        print("Cleaning in progress...")
        print('...')
        clean()
        print("Cleaning complete.")


def clean():
    """Clean the working directory and reset files back to their starting
       positions.
    """
    # Note, if properly handling exceptions and errors, and also maybe using
    # temporary file systems, this method could become obsolete. That would be
    # a good thing!
    pass


def strip_chars(directory):
    """Strip leading characters from file names in a specified directory. 

    Pattern is of the form 'job_####', where '#' can be any number of 
    numbers, but usually less than five.

    Function should return None if operations successful, or a list of
    bad file names if any are found.
    """
    # Check syntax for backslashes - compile to \\w and \\d
    name_RE = re.compile('^job_[\d]*[\s]{1}')
    file_list = os.listdir(directory)
    # Consider using if foo.startswith('job_#### ') or foo.endswith(xxxx) to
    # check for string prefixes or suffixes. Cleaner and less error prone.
    for f in file_list:
        if f.startswith('job'):
            new = re.split(name_RE, f)[1]
            # remember to join paths, if you're not working from that directory

            os.rename(os.path.join(directory, f), os.path.join(directory, new))
        else:
            continue
    return


#***************#
# CoC Collector #
#***************#

def collect_cocs(directory, file_list):
    """Collects Chain of Custody files given a target directory and list of
       files to match against CoCs.
    """

#******************#
# Report Collector #
#******************#
# Standard coc filename len = 13 --> 123456coc.pdf
# Multi-PDF coc filename len = 17 --> 123450-456coc.pdf
# Single rerun coc filename len = 14 --> 123456acoc.pdf
# Multi-PDF rerun coc filename len = 19 --> 123450a-456acoc.pdf
# QC/WP/SP samples have NO RANGES, but take the form QC###-###coc.pdf. len = 16


def main():

    parser_setup()

    # Make system checks
    if system_checks() == False:
        print("System checks failed. Program exiting.")
        sys.exit(1)
    elif file_check() == False:
        print("No files exist in the reviewed reports folder for collation.")
        print("Program exiting.\n")
        sys.exit(0)

    print("Checking CoC names...")
    name_check(AUS_COCS, CORP_COCS)
    print()
    print("Analyzing file names...")
    strip_chars(REVD_REPORTS)


if __name__ == '__main__':
    main()
