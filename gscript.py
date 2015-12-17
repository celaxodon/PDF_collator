#!/usr/bin/env python3

"""Test script for invoking ghostscript by subprocess

Question 1: Where does the report wind up  when we just collate with
ghost script without caring about the directory?
"""

import subprocess
import os.path

from PDF_collator import strip_chars, total_file_size

REVD_REPORTS = '/Users/klurl/ASI_Work/Scripts/PDF_collator/functional_tests/Reviewed'
FIN_REPORTS = '/Users/klurl/ASI_Work/Scripts/PDF_collator/functional_tests/Complete'

def invoke_gs(report_name, dictionary):
    # Name only because we're moving to the REVD_REPORTS first!
    gs_list = [x for x in dictionary['pdfs']]
    # Generate full paths to Reviewed and stripped pdf files
    #gs_list = os.path.join(REVD_REPORTS, x) for x in dictionary['pdfs']]
    gs_list.append(dictionary['coc']) # COC goes last in the report

    # Location of final report - though we could just os.chdir to the FIN_REPORTS
    # folder before running this function.
    #final_report = report_name
    final_report = os.path.join(FIN_REPORTS, report_name)
    
    #gs -dBATCH -dNOPAUSE -q -sDEVICE=pdfwrite -dAutoRotatePages=/PageByPage -sOutputFile="$FILENAME" ./*.pdf 2>/dev/null;
    command = ["gs",
               "-q",
               "-sDEVICE=pdfwrite",
               "-dAutoRotatePages=/PageByPage",
               "-sOutputFile=%s" % final_report,
               # csv or space-separated both report file name too long
               " ".join(gs_list)]

    # Need to handle stdout and stderr
    subprocess.Popen(command)

### Start script ###

cwd = os.getcwd()

# Clear names if raw pdfs
strip_chars(os.path.join(cwd, 'functional_tests/Reviewed'))
pdfs = os.listdir(os.path.join(cwd, 'functional_tests/Reviewed'))
pdfs.sort()

# os.chdir(<finished reports>)
report_name = "564894-898.pdf"
dictionary = {'coc': os.path.join(cwd, 'functional_tests/COCs/Aus/564894-898coc.pdf'),
              'pdfs': pdfs,
              'missing': None}

invoke_gs(report_name, dictionary)
