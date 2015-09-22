#!/usr/bin/env python3

#---------------------------------------#
#           PDF Collator v.01           #
#        Written by Graham Leva         #
#     Copyright (c) 2015 AnalySys, Inc. #
# Something about the proper license    #
#---------------------------------------#

import sys, os.path, logging, argparse, re
# For color output
import colorama

#***********#
# Variables #
#***********#

# Location for finished, collated reports
FIN_REPORTS = ''
# Location for reports that have been reviewed, but not collated
REVD_REPORTS = ''
# Location of CoCs
COC_DIR = ''
# Folder to copy reports into after collation
BILLINGS = ''


def system_checks():
    """ Function for checking required software is installed
        and that remote file system directories are mounted """

    # Check for OS version for compatibility
    # Try block?

    if os.path.exists('/Volumes/Data/') != True:
        print("This program cannot run unless you have the 'Data' folder mounted.")
        print("Please connect to the file server (New Server) and run this\
               program again.")
        return
    elif os.path.exists('/Volumes/scans/') != True:
        print("This program cannot run unless you have the 'scans' folder mounted.")
        print("Please connect to the file server (New Server) and run this\
               program again.")
        return
    else os.path.exists('/Volumes/Admin/') != True:
        print("This program cannot run unless you have the 'Admin' folder mounted.")
        print("Please connect to the file server (New Server) and run this\
               program again.")
        return

    # Test that specific directories exist
    for folder in [FIN_REPORTS, REVD_REPORTS, COC_DIR, BILLINGS]:
        if os.path.exists(folder) != True:
            print("The folder {0} is not accessible. Please make sure you can\
                   navigate to the folder before running this\
                   program again.".format(folder))
            return
        else:
            continue

    # Test for files existing in REVD_REPORTS - if none exist, program exits
    # Reconsider where to put this check and overall flow for system_checks func.
    if len(os.listdir(REVD_REPORTS)) == 0:
        return "No files exist in the reviewed reports folder. Program exiting."


# Argument parser for command line invocation
def parser_setup():
    parser = argparse.ArgumentParser(description='Rename scanned reports, find Chain of Custodies (CoCs) and collate PDF reports.')
    # -h, --help is setup by default
    parser.add_argument('-c', '--clean', help="Clean up temporary directories and\
                        reset files to starting positions.", action="store_true")
    args = parser.parse_args()
    if args.clean:
        # do something
        print("Cleaning in progress...")
        clean()
        print()
        print("Cleaning complete.")


def clean():
    """ Clean the working directory and reset files back to their starting
        positions. """
    pass

#***************#
# Name Stripper #
#***************#

def strip_chars(directory):
    """ Strip leading characters from file names in a specified directory. 
        Pattern is of the form 'job_####', where '#' can be any number of 
        numbers, but usually less than five."""

    regex = re.compile('job_[\d]*')

    for item in os.path(directory):
        if str(filename)[0:4] == 'job_':
            #os.rename(<src>, <dest>)



#***************#
# CoC Collector #
#***************#
# Standard coc filename len = 13 --> 123456coc.pdf
# Multi-PDF coc filename len = 17 --> 123450-456coc.pdf
# Single rerun coc filename len = 14 --> 123456acoc.pdf
# Multi-PDF rerun coc filename len = 19 --> 123450a-456acoc.pdf
# QC/WP/SP samples have NO RANGES, but take the form QC###-###coc.pdf. len = 16

#******************#
# Report Collector #
#******************#

# "Main" when running by itself. Should be the default operating mode, since
# users are simply clicking on the script to execute
if __name__ == '__main__':

    # Check for required file system locations and mount points
    system_checks()
    # Set up CLI argument parser
    parser_setup()
    # Test whether files exist before running name stripper.
    try:
        # If files exist, run program

    except:
        # Some exception for files not existing
