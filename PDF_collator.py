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


def collect_cocs(coc_list, A_set, B_set, pdf_name):
    """Collects Chain of Custody files given a sequence of target directories
    and list of valid files to match against CoCs.

    Standard coc filename --> 123456coc.pdf
    Multi-PDF coc filename --> 123450-456coc.pdf
    Single rerun coc filename --> 123456acoc.pdf
    Multi-PDF rerun coc filename --> 123450a-456acoc.pdf
    *QC/WP/SP samples have NO RANGES, but take the form QC###-###coc.pdf.

    Returns Chain of Custody path if CoC found, or None.
    """

    # Fix this - imprecise. Basically using it as a symbolic constant

    # Search for pdf in CoC directories
    # Reconsider search algorithm - that's what it is.
    pattern = pdf_name[:-7]
    for i in A_set.union(C_set):
        if i.startswith(pattern):
            if i in A_set:
                coc = os.path.join(dir1, i)
                break
            else:
                coc = os.path.join(dir2, i)
                break
        else:
            coc = None

    return coc
                

def backcheck(coc_name, file_list):
    """Checks the list of numbers indicated by the CoC file name to make sure
    the ranges a CoC represents are really present in the pdf directory.
    
    Returns the list of required PDFs and 'None' if there are no missing pdfs
    from the ranges indicated; otherwise returns the missing numbers in a list.
    Should not be used with QC/SP/WP samples.
    """

    required_pdfs = set(get_ranges(coc_name))

    # Construct a set of present pdfs, taking off the 'pg?.pdf' suffixes
    file_set = set([f[:-7] for f in file_list])

    # Want to check that all files, as indicated by get_ranges, are present
    # in the file_set. Extra files not in required_pdfs will be present!
    if required_pdfs.issubset(file_set):
        missing_pdfs = None
        return list(required_pdfs), missing_pdfs
    else:
        missing_pdfs = list(required_pdfs.difference(file_set))
        return list(required_pdfs), missing_pdfs


def get_ranges(coc_name):
    """Return a list of ranges from a range coc string.

    For example, '123456-460coc.pdf' would return:
        ['123456', '123457', '123458', '123459', '123460']

    and '123456a-458acoc.pdf' would return:
        ['123456a', '123457a', '123458a']
    """

    # Cut 'coc.pdf'
    r = coc_name[:-7]
    if '-' in r:
        first, last = r.split('-')
        last = first[:3] + last
    # No range at all - single number CoC
    else:
        return [r]

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


def total_file_size(directory):
    """Return the size of the files present in a given directory in bytes"""

    total_size = 0

    # Note that os.path.getsize() is equivalent to instantiating an os.stat
    # object and calling st_size. Just looks cleaner this way.
    try:
        for f in os.listdir(directory):
            total_size += os.path.getsize(f)
    except OSError:
        print("File {0} could not be found".format(f))

    return total_size


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
        print("The following PDFs do not match the correct naming scheme "
              "and will be ignored:")
        print("--------------------")
        for name in bad_pdf_names:
            print(name)
        print("--------------------")

#########
#   Dict structure:
#   assign names to files:
#     '<report_name>': {'coc': '/some/path/to/123456coc.pdf',
#                       'pdfs': [list, of, pdfs, for, coc]
#                      }
#########

    # Collect and analyze PDFs vs. CoCs
    print()
    print("Searching for and matching CoCs...")

    missing_coc_pdfs = []
    # Start recursive function ('aggregator') taking as arguments:
    #    missing_coc_pdfs -- a list of pdfs for which no coc was found
    #    good_pdf_names -- a list used as a stack
    #    dict of all necessary info
    # Should return list of missing cocs, report names + coc names + ranges of numbers
    pdf_stack = good_pdf_names[:]
    A_set = set(os.listdir(AUS_COCS)) # Austin dir
    A_set.discard('.DS_Store')
    C_set = set(os.listdir(CORP_COCS)) # Corpus dir
    C_set.discard('.DS_Store')
    coc_list = list(A_set.union(C_set))
    i = 0
    while pdf_stack != []:  # May need a different increment
        # Calculate for QC/SP/WP samples, too
        # by collect_cocs searching for a single pdf's value every time,
        # we build and rebuild sets of the CoCs as many times as there
        # are CoCs to find... It would be better if we built it just once
        coc = collect_cocs(coc_list, A_set, C_set, pdf_stack[i])

        # CoC not found! Pop searched for pdf out of stack and into missing_coc_pdfs
        if coc == None:
            missing_cocs += list(pdf_stack.pop(i))
            # call the function again with pdf_stack and missing_coc_pdfs as args
            pass
        else:
            coc_name = os.path.basename(coc)

        # It's a QC/SP/WP sample - no range check
        # ONLY accounting for one pdf with a QC/SP/WP sample - is that accurate?
        if coc_name.startswith(('QC', 'WP', 'SP')):
            report_name = coc_name.replace('coc', '')
            pdfs = pdf_stack[i]
            # backcheck necessary?
            # Add dictionary entry with necessary info
            # report, coc_name, coc_path ('coc'), required pdfs
            # pop required_pdfs out of the stack -- all present
            pdf_stack.remove(pdf_stack[i])
            # Call the function again with params
            pass
        elif '-' in coc_name: # Range sample
            report_name = coc_name.replace('coc', '')
            required_pdfs, missing_pdfs = backcheck(coc_name, pdf_stack)
            if missing_pdfs != None:
                # All PDFs found!
                # pop out other values from stack of good names
                #good_pdf_names.remove(reverse_match)
                #<recursive_fn_call>(good_pdf_names)
            # '123456coc.pdf' --> '123456.pdf'
            report_name = coc.replace('coc', '')
        else: # Single CoC
            report_name = coc_name.replace('coc', '')
            required_pdfs, missing_pdfs = backcheck(coc_name, pdf_stack

    # After recursive function
    if missing_cocs != []:
        print("The following files could not be matched with a CoC.")
        print("Please check that the CoCs exist before running this program "
              "again.\n")
        print("--------------------")
        for num in missing_cocs:
            print(num)
        print("--------------------")


if __name__ == '__main__':
    main()
