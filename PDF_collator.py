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
        print()
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
        if os.path.exists(os.path.join('/Volumes', d)): # Directory is mounted
            continue
        else:
            print()
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

    return True


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
            match = coc_RE.fullmatch(i)
            # Full match exists!
            if match is not None:
                if i.startswith(("QC", "SP", "WP")):
                    # Don't worry about ranges for these samples.
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

    Function should return a tuple consisting of a list of the directory's
    contents (valid names only) and either None, in the event that no bad
    file names were found, or a list of bad file names if any were found.
    """
    prefix_RE = re.compile('^job_[\\d]*[\\s]{1}')
    name_RE = re.compile('^[\\d]{6}pg[1-9]{1}\\.pdf$')

    # New operations
    i = 0
    bad_file_names = []
    dirlist = os.listdir(directory)
    while i < len(dirlist):
        if dirlist[i].startswith('job'):
            try:
                new = re.split(prefix_RE, dirlist[i])[1]
                os.rename(os.path.join(directory, dirlist[i]),
                          os.path.join(directory, new))
                # Update the list with new name
                dirlist[i] = new
                # Check validity of new name
                if not name_RE.fullmatch(dirlist[i]):
                    bad_file_names.append(dirlist[i])
                i += 1
            except IndexError:
                bad_file_names.append(dirlist[i])
                i += 1
        else:
            if not name_RE.fullmatch(dirlist[i]):
                bad_file_names.append(dirlist[i])
            i += 1

    #Get a set of only valid names in the directory
    valid_names = list(set.difference(set(dirlist), set(bad_file_names)))
    if len(bad_file_names) == 0:
        return (valid_names, None)
    else:
        return (valid_names, bad_file_names)


def collect_cocs(*args, file_list):
    """Collects Chain of Custody files given a sequence of target directories
    and list of valid files to match against CoCs.

    Standard coc filename len = 13 --> 123456coc.pdf
    Multi-PDF coc filename len = 17 --> 123450-456coc.pdf
    Single rerun coc filename len = 14 --> 123456acoc.pdf
    Multi-PDF rerun coc filename len = 19 --> 123450a-456acoc.pdf
    QC/WP/SP samples have NO RANGES, but take the form QC###-###coc.pdf. len = 16

    Returns None if all pdfs were matched with CoCs and back matching was
    successful. Otherwise returns a list of PDFs for which no CoC could be
    matched.

    Throws an error in the event that back matching CoCs won't be entirely matched.
    Asks the user to approve or disapprove collation without all pdfs matching
    the CoC range.
    """
    coc_dict = {}

    # Should be accounted for with strip_chars() function since it also
    # checks names and returns a valid list
    #if '.DS_Store' in file_list:
    #    file_list.remove('.DS_Store')

#    When PDFs are matched to CoCs, pop them out of the list stack so the user
#    can know what PDFs didn't match.
    # Construct the dictionary of CoCs
    for folder in args:
        for k in os.listdir(folder):
            coc_dict[k] = None

    for f in file_list:


def get_ranges(string):
    """Return a list of ranges from a range coc string.

    For example, '123456-460coc.pdf' would return:
    [123456, 123457, 123458, 123459, 123460]

    and '123456a-458acoc.pdf' would return:
    [123456a, 123457a, 123458a]
    """

    # Cut 'coc.pdf'
    r = string[:-7]
    first, last = r.split('-')
    last = first[:3] + last

    # handle rerun versus normal range CoC
    if first.isnumeric():
        first = int(first)
        last = int(last) + 1

        # Check for 1000s rollover (e.g. ...995-002)
        if last < first:
            last += 1000

        return [str(x) for x in list(range(first, last))]
    # Rerun sample (e.g. 123456a-460a)
    else:
        # strip rerun characters off end
        rerun_char = first[-1:]
        first = int(first[:-1])
        # Account for range() stopping at last, instead of including
        last = int(last[:-1]) + 1

        # Check for 1000s rollover (e.g. ...995-002)
        if last < first:
            last += 1000

        return [(str(x) + rerun_char) for x in list(range(first, last))]



#******************#
# Report Collator  #
#******************#
# To do

def main():

    parser_setup()

    # Make system checks
    print("Performing system checks...", end=" ")
    if system_checks():
        print("Passed.")
    else:
        print()
        print("System checks failed. Program exiting.")
        sys.exit(1)

    file_check_val = file_check()
    if file_check() == False:
        print("No files exist in the reviewed reports folder for collation.")
        print("Program exiting.\n")
        sys.exit(0)

    # Check CoC file names
    print()
    print("Analyzing CoC names...")
    bad_coc_names = name_check(AUS_COCS, CORP_COCS)
    if bad_coc_names is not None:
        print("The following CoCs have been improperly named. Please correct "
              "before running this program again.")
        for name in bad_coc_names:
            print(name)
        sys.exit(1)

    # Get rid of job_#### prefixes and check namings
    print()
    print("Analyzing and fixing file names...")
    good_pdf_names, bad_pdf_names = strip_chars(REVD_REPORTS)
    if bad_pdf_names != None:
        print("An error has occured when stripping file names!")
        print("The following CoCs do not match the correct naming scheme "
              "and will be ignored:")
        print("--------------------")
        for name in bad_pdf_names:
            print(name)
        print("--------------------")

    # Collect and analyze PDFs vs. CoCs
    print()
    print("Searching for and matching CoCs...")
    collect_cocs(AUS_COCS, CORP_COCS, good_pdf_names)


if __name__ == '__main__':
    main()
