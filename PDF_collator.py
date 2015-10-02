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
FIN_REPORTS = '/Volumes/Data/Data Review/8. Completed Reports to File/'
# Location for reports that have been reviewed, but not collated
REVD_REPORTS = '/Volumes/Data/Data Review/5. Data Qual Review Complete/'
# Location of CoCs
COC_DIR = '/Volumes/scans/!Current COC/'
# Folder to copy reports into after collation
BILLINGS = '/Volumes/Admin/Billings/'


def system_checks():
    """Check required software is installed and that remote file system
    directories are mounted.
    """
    # Check operating system
    if os.uname().sysname != 'Darwin':
        print("Warning! This program was only designed to run on Mac OS X")
        ans = input("Run at your own risk. Continue? (y/n)\n")
        while True:
            low_ans = str(ans).lower()
            if low_ans == 'y' or low_ans == 'yes':
                # Continue with checks
                break
            elif low_ans == 'n' or low_ans == 'no':
                return False
            else:
                print("Yes ('y') or no ('n'), please.")
                ans = input("Continue program? (y/n)\n")

    # Check correct volumes from file server mounted
    elif os.path.exists('/Volumes/Data/') == False:
        print("This program cannot run unless you have the 'Data' folder "
              "mounted.")
        print("Please connect to the file server (\'New Server\') and run this"
              " program again.\n")
        return False

    elif os.path.exists('/Volumes/scans/') == False:
        print("This program cannot run unless you have the 'scans' folder "
              "mounted.")
        print("Please connect to the file server (\'New Server\') and run this"
              " program again.\n")
        return False

    elif os.path.exists('/Volumes/Admin/') == False:
        print("This program cannot run unless you have the 'Admin' folder "
              "mounted.")
        print("Please connect to the file server (\'New Server\') and run this" 
               "  program again.\n")
        return False
    else:
        return True

    # Test that specific directories exist
    for folder in [FIN_REPORTS, REVD_REPORTS, COC_DIR, BILLINGS]:
        if os.path.exists(folder) == False:
            print("The folder {0} is not accessible. Please make sure you can"
                  " navigate to the folder before running this"
                  " program again.\n".format(folder))
            return False
        else:
            continue


def file_check(directory):
    """Test for files existing in target directory."""
    if len(os.listdir(directory)) == 0:
        print("No files exist in the reviewed reports folder for collation.\n")
        return False
    else:
        return True    # Files exist

    # Consider checking for .afp_[\d]+ files in collation directory


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
        print("No files found to collate. Program exiting.")
        sys.exit(0)

    print("Analyzing file names...")
    strip_chars(REVD_REPORTS)


# "Main" when running by itself. Should be the default operating mode, since
# users are simply clicking on the script to execute
if __name__ == '__main__':

    main()
