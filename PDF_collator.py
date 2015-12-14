#!/usr/bin/env python3

#-----------------------------------------#
#            PDF Collator v.01            #
#          Written by Graham Leva         #
#     Copyright (c) 2015 AnalySys, Inc.   #
#    Something about the proper license   #
#-----------------------------------------#

#    Standard coc filename --> 123456coc.pdf
#    Multi-PDF coc filename --> 123450-456coc.pdf
#    Single rerun coc filename --> 123456acoc.pdf
#    Multi-PDF rerun coc filename --> 123450a-456acoc.pdf
#    *QC/WP/SP samples have NO RANGES, but take the form QC###-###coc.pdf.

import sys
import subprocess
import os
import os.path
import logging
import re
import argparse


# Location for finished, collated reports
FIN_REPORTS = ''
# Location for reports that have been reviewed, but not collated
REVD_REPORTS = ''
# Location of CoCs
AUS_COCS = ''
CORP_COCS = ''
PT_COCS = ''
# Folder to copy reports into after collation
BILLINGS = ''


def system_checks():
    """Check required software is installed and that remote file system
    directories are mounted.

    Checks for the following:
      - System is OS X
      - Required network drives are mounted
      - Specific directories exist on filesystem
      - Ghostscript install is present on the machine

    Returns `False` in the event that any of the checks fail. Users
    can override the OS X requirement.
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

    # Test for ghostscript executable
    # Download OS X version from http://pages.uoregon.edu/koch/
    # At time of writing, 9.18 was the current version
    gs_download = 'http://pages.uoregon.edu/koch'
    gs_path = '/usr/local/bin/gs'

    if not os.path.exists(gs_path):
        print("The ghostscript program is needed for report collation."
              " Please download it from {0}, install it  and rerun this"
              " program.".format(gs_download))
        return False

    return True


def file_check(directory):
    """Test existence of files for collation in target directory.

    Takes as argument a target `directory` to check for files in.

    Returns True if files exist and are relevant or False if
    either no files exist or files that exist are irrelevant (e.g.,
    system-specific files like .DS_Store).
    """
    # Consider checking for .afp_[\d]+ files in collation directory

    if len(os.listdir(directory)) == 0:
        return False
    elif len(os.listdir(directory)) == 1 and '.DS_Store' in os.listdir(directory):
        return False
    else:
        return True    # Files exist and they're relevant


def name_check(*args):
    """Test for incorrect Chain of Custody labels before running each time.

    Takes as arguments a series of directories to check CoC syntax.

    Returns a list of bad file names, or None, if name check passes.
    """

    bad_names = []
    coc_list = []
    # Get list of all COCs
    for path in args:
        coc_list.extend(os.listdir(path))
        # Remove OS X-specific directory services store file
        #clean_list = list(filter(lambda x: x != '.DS_Store', coc_list))
        if '.DS_Store' in coc_list:
            coc_list.remove('.DS_Store')

    # Need to account for repeat files - 400-400coc.pdf
    # What if two reports needing the same file. Different function - find_cocs
    # Need to account for report ranges decrementing instead of incrementing.
    coc_RE = re.compile('([\\d]{3}([\\d]{3})([a-d]{1})?(-([\\d]{3})(\\3)?)?coc\\.pdf$|(QC|WP|SP)([\\d]{3})-([\\d]{3})coc\\.pdf$)')

    for i in coc_list:
        match = coc_RE.fullmatch(i)
        # Full match exists!
        if match:
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

    if bad_names:
        return (bad_names, coc_list)
    else:
        return (None, coc_list)
                

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
    return NotImplementedError


def strip_chars(directory):
    """Strip leading characters from file names in a specified directory. 

    Pattern is of the form 'job_####', where '#' can be any number of 
    numbers, but usually less than five, followed by a single space.

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
    if bad_file_names:
        return (valid_names, bad_file_names)
    else:
        return (valid_names, None)


def find_coc(coc_list, coc_tuple, pdf_name):
    """Finds and returns location of Chain of Custody files given a
    sequence of target directories and list of valid files to match
    against CoCs.

    Arguments:
        'coc_list' - a list of CoCs that have already been checked for
                     syntax mistakes.
        'coc_tuple' - a tuple consisting of three sets, used for finding
                      the location of a coc in the filesystem:
                        * 'A_set' - Set of Austin CoCs.
                        * 'C_set' - Set of Corpus CoCs.
                        * 'P_set' - PT sample CoCs.
        'pdf_name' - A single pdf to match it against

    Returns path to Chain of Custody if the CoC was found, or 'None' in
    the event that it was not (e.g., '/path/to/123456coc.pdf').
    """
    # Search for pdf in CoC directories
    # Reconsider search algorithm - that's what it is.
    pattern = pdf_name[:-7]
    for i in coc_list:
        if i.startswith(pattern):
            if i in coc_tuple[0]:
                # Austin CoC dir
                return os.path.join(AUS_COCS, i)
            elif i in coc_tuple[1]:
                # Corpus CoC dir
                return os.path.join(CORP_COCS, i)
            else:
                # PT CoC dir
                return os.path.join(PT_COCS, i)
        else:
            return None


def backcheck(coc_name, file_list):
    """Checks the list of numbers indicated by the CoC file name to make sure
    the ranges a CoC represents are really present in the pdf directory.
    
    Returns the list of required PDFs and 'None' if there are no missing pdfs
    from the ranges indicated; otherwise returns the missing numbers in a list.
    """

    #QC --> ('QC123-456')
    #multi --> ('123456', '123457', ...)
    #Single --> ('123456')
    required_pdfs = get_ranges(coc_name)

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
    """Return a set of ranges from a range coc string.

    'coc_name' - A range coc name, like '123456-470coc.pdf'.

    For example, '123456-460coc.pdf' would return:
        ['123456', '123457', '123458', '123459', '123460']

    and '123456a-458acoc.pdf' would return:
        ['123456a', '123457a', '123458a']

    Return a list of ranges in the event that ranges are indicated in the CoC
    name. If there are no ranges (like with QC/WP/SP samples or for single
    number CoCs), return the number itself.
    """

    # Cut 'coc.pdf'
    r = coc_name[:-7]
    if r.startswith(('QC', 'WP', 'SP')):
        return {r}
    elif '-' in r:
        first, last = r.split('-')
        last = first[:3] + last
    # No range at all - single number CoC
    else:
        return {r}

    # handle rerun versus normal range CoC
    if first.isnumeric():
        first = int(first)
        last = int(last) + 1

        # Check for 1000s rollover (e.g. ...995-002)
        if last < first:
            last += 1000

        return set(str(x) for x in list(range(first, last)))
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

        return set((str(x) + rerun_char) for x in list(range(first, last)))


# May need an initial list for missing_coc_list
def aggregator(missing_coc_list, pdf_stack, report_dict={}):
    """Function takes in a list of missing cocs, stack of good pdf
    names, and dictionary for collecting reports recursively. Returns two
    variables: (1) a list of pdfs for which chains could not be
    found or 'None' in the case that all CoCs were found for PDFs, and
    (2) a dictionary consisting of dictionaries whose keys are the report
    names and values are CoC location, the associated pdfs and missing pdfs
    after being back-checked from the coc range.

    Takes as input
        'missing_coc_list' - an initially empty list of missing chain of
                             custodies,
        'pdf_stack' - a list of good single-page pdf names (already
                      sanitized), which is used as a stack,
        'report_dict' - a dictionary consisting of report names, followed
                        by a nested dict of info relating to that report.

    Example return report dictionary:

    {'123456-458.pdf': {'coc': '/path/to/123456-458coc.pdf',
                        'pdfs': ['123456pg1.pdf', '123457pg1.pdf'],
                        'missing_pdfs' = ['123458']}
    }

    The list of missing cocs is added to whenever a coc cannot be found for
    a given PDF, and the pdf stack is reduced for two reasons:
        - when a pdf cannot be matched to a CoC, and
        - when a series of pdfs match to a given coc range (back checking)
    """

    i = 0
    while pdf_stack:
        # What about these function variables? Are globals a good idea?
        # May not be able to test...
        # This isn't good and needs work. No access to `coc_list` here.
        coc = find_coc(coc_list, A_set, C_set, P_set, pdf_stack[i])

        # CoC not found!
        if coc == None:
            missing_coc_list += pdf_stack.pop(i)
            aggregator(missing_coc_list, pdf_stack, report_dict)

        coc_name = os.path.basename(coc)
        report_name = coc_name.replace('coc', '')
        required_pdfs, missing_pdfs = backcheck(coc_name, pdf_stack)
        matched_pdfs = []

        # get file names (not just nums) for PDFs that match to CoCs
        for j in required_pdfs:
            for k in pdf_stack:
                if k.startswith(j):
                    matched_pdfs.append(k)
        # Remove pdfs from pdf stack
        # Consider using sets and recreating the pdf_stack...
        for f in matched_pdfs:
            pdf_stack.remove(f)

        if missing_pdfs:
            report_dict[report_name] = {'coc': coc,
                                        'pdfs': matched_pdfs,
                                        'missing_pdfs': missing_pdfs}
            aggregator(missing_coc_list, pdf_stack, report_dict)
        else:
            # Should I pass missing_pdfs = None just so each entry has
            # the variable?
            report_dict[report_name] = {'coc': coc, 'pdfs': matched_pdfs}
            aggregator(missing_coc_list, pdf_stack, report_dict)




    return missing_coc_list, report_dict


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

def collate(dictionary):
    # Use the dictionary.keys() method to create a list of keys, then
    # for each key, pop it out of the dictionary.
    for report in list(dictionary.keys()):
        #unpack dictionary
        dictionary.pop(report)
    #
    # CoC needs to go last in collation
    subprocess.call(["gs", [options], pdf_list, "coc"])
    # Args from shell version:
    # -o
    #     -dBATCH [implied]
    #     -dNOPAUSE [implied]
    # -q
    # -sDEVICE=pdfwrite
    # -dAutoRotatePages=/PageByPage
    # -sOutputFile=<reportname>
    # ./*.pdf (grouped all pdfs in order in one directory)
    # 2>/dev/null
    #
    # Maybe also return the reportname, followed by size and compression
    # stats?
    return NotImplementedError


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

    if file_check(REVD_REPORTS) == False:
        print("No files exist in the reviewed reports folder for collation.")
        print("Program exiting.\n")
        sys.exit(0)

    # Check CoC file names
    print()
    print("Analyzing CoC names...")
    bad_coc_names, coc_list = name_check(AUS_COCS, CORP_COCS)
    if bad_coc_names:
        print("The following CoCs have been improperly named. Please correct "
              "the file names before running this program again.")
        for name in bad_coc_names:
            print(name)
        sys.exit(1)

    # Get rid of job_#### prefixes and check namings
    print()
    print("Analyzing and fixing PDF names...")
    good_pdf_names, bad_pdf_names = strip_chars(REVD_REPORTS)
    if bad_pdf_names:
        print("An error has occured when stripping file names!")
        print("The following PDFs do not match the correct naming scheme "
              "and will be ignored:")
        print("--------------------")
        for name in bad_pdf_names:
            print(name)
        print("--------------------")

    # Collect and analyze PDFs vs. CoCs
    print()
    print("Searching for and matching CoCs...")

    # Sets used as input to find_coc fn for faster lookups
    # The same operation is done in name_check... can it
    # return the lists?
    A_set = set(os.listdir(AUS_COCS)) # Austin dir
    A_set.discard('.DS_Store')
    C_set = set(os.listdir(CORP_COCS)) # Corpus dir
    C_set.discard('.DS_Store')
    P_set = set(os.listdir(PT_COCS)) # dir for PT (QC/WP/SP) samples
    P_set.discard('.DS_Store')

    # coc_list is being sort of used as a global here. Following functions
    # (aggregator) should still have it in their namespaces.
    coc_list = list(A_set.union(C_set).union(P_set))
    coc_tuple = (A_set, C_set, P_set)

    pdf_stack = good_pdf_names[:]    # Necessary?
    # The list of all pdfs for which no CoC could be found
    missing_coc_list = []
    missing_coc_list, report_dict = aggregator(missing_coc_list, pdf_stack)

    # Get user's consent to continue execution, despite missing PDFs being
    # detected.
    if missing_coc_list:
        print("The following files could not be matched with a CoC.")
        print("Please check that the CoCs exist before running this program "
              "again.\n")
        print("--------------------")
        for num in missing_coc_list:
            print(num)
        print("--------------------")
        ans = input("Do you want to continue with other reports? (y/n)\n")
        while True:
            lower_ans = str(ans).lower()
            if lower_ans == 'y' or lower_ans == 'yes':
                # Continue with checks
                break
            elif lower_ans == 'n' or lower_ans == 'no':
                sys.exit(0)
            else:
                print("Yes ('y') or no ('n'), please.")
                ans = input("Continue program? (y/n)\n")
    else:
        # Not yet written - need to collect and collate
        pass
    # Copy final report to "BILLINGS"

if __name__ == '__main__':
    main()
