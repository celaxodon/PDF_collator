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

#***********#
# Variables #
#***********#

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
    """Test for files existing in target directory."""
    if len(os.listdir(directory)) == 0:
        return False
    elif len(os.listdir(directory)) == 1 and '.DS_Store' in os.listdir(directory):
        return False
    else:
        return True    # Files exist and they're not irrelevant

    # Consider checking for .afp_[\d]+ files in collation directory
    # and for .DS_Store files.


def name_check(*args):
    """Test for incorrect Chain of Custody labels before running each time.
    
    Returns a list of bad file names, or None, if name check passes.
    """

    bad_names = []
    # Fix me!
    # Need to account for repeat files - 400-400coc.pdf
    # Need to account for two reports needing the same file. Different function - find_cocs
    # Need to account for report ranges decrementing instead of incrementing.
    # Need to account for rerun coc naming errors (e.g. 123456a-460coc.pdf, 1234556-460acoc.pdf)
    coc_regex = '([\d]{6}[a-d]?(-[\d]{3}[a-d]?)?coc\.pdf|(QC|WP|SP)[\d]{3}-[\d]{3}coc\.pdf)'

    for path in args:
        coc_list = os.listdir(path)
        if '.DS_Store' in cocs:     # Remove OS X-specific directory services store file
            coc_list.remove('.DS_Store')   
        for i in cocs:
            # Check against regex for non-conforming file names 
            if re.match(coc_regex, i):
                continue
            # Check that first range number doesn't match the second
            elif '-' in i:
                if 
            else:
                # Throw a warning
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

#***************#
# Name Stripper #
#***************#

def strip_chars(directory):
    """Strip leading characters from file names in a specified directory. 

    Pattern is of the form 'job_####', where '#' can be any number of 
    numbers, but usually less than five.
    """
    # Check syntax for backslashes - compile to \\w and \\d
    regex = re.compile('^job_[\d]*[\w]{1}')
    file_list = os.listdir(directory)
    # Consider using if foo.startswith('job_#### ') or foo.endswith(xxxx) to
    # check for string prefixes or suffixes. Cleaner and less error prone.
    for i in file_list:
        if i.startswith('job'):
            # remember to join paths, if you're not working from that directory

            os.rename(old, new)
        else:
            continue


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

    print("Analyzing file names...")
    strip_chars(REVD_REPORTS)


# "Main" when running by itself. Should be the default operating mode, since
# users are simply clicking on the script to execute
if __name__ == '__main__':

    main()
