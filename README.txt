                                PDF_collator README
                              written by: Graham Leva
                             last updated: June 1, 2015


This document notes design decisions and usage patterns for the project
entitled "PDF_collator".

The PDF_collator script was originally designed as a stopgap measure to collate
individual PDF pages produced by the Laboratory Information Management System 
(LIMS). The Script still fulfills this purpose, but additional features have 
been added over time. At this point, the script should probably be rewritten in 
Python or another high-level language for readability.


### FEATURES ###

As of June 1, 2015, the script does the following:
  * Checks that necessary filesystems have been mounted. 
  * Searches for and collects Chain of Custody (COC) PDFs matching reports 
    produced by the LIMS that have been reviewed for data integrity.
  * Checks that the full range of files, as indicated by the COC naming scheme.
    If the full range is not found, a warning is printed to the screen, but it
    proceeds with the collation anyway. 
  * Performs rudimentary error checking on COC files. This is complemented by a
    cron job run daily to make sure COC file naming is accurate.
  * Creates temporary directories, reorders COC PDFs last and report files 
    first.
  * Uses Ghostscript to collate reports and reduce their final size.
  * Removes temporary directories, disposes of files after collation, and moves 
    reports to appropriate location. 
  * Has a reset function to cleanup the temporary directory system. This returns
    files to their original location, based on filename. Only needs to be used if
    COC files are improperly named. 


### DESIGN NOTES ###

    Ghostscript was chosen as an alternative to the previous solution, which
used an Apple script. The issue it has (somewhat) successfully 
addressed is file size and rotation of PDFs, where the Apple script fails on 
both.
    The previous choice was using Apple's automator software, and used
a python script located in '/System/Library/Automator/Combine\ PDF\ Pages.action/Contents/Resources/join.py'. This was a poor design choice, 
as the script caused collated PDFs to balloon in size (26.5MB instead
of 6MB, for example). 
    Ghostscript is fast and accurate, but doesn't take input well.
Both piping input into gs and an array with PDF titles (in the local 
directory) were attempted, but both failed. So far, the only syntax 
gs recognizes for multiple pdf inputs is to either list them, as so:
   
 <gs script here> pdf1.pdf pdf2.pdf ... 

or 

 <gs script here> files*pdf  

    Also, output locations don't seem to be able to be specified, though that could be a syntax issue. (check)

    An alternative to Ghostscript might be the Python 3.x library, 
PyPDF2, though it hasn't been thoroughly analyzed for suitability yet.


### USAGE ###

PDF_collator [OPTIONS] Collates reviewed data PDFs with their matching Chain of 
                       Custody files. Final reports are filed for both billing
                       and delivery to clients. 

OPTIONS:
  -h, --help Prints the usage guide

  -r, --reset Resets pdfs and their associated Chain of Custody (CoC) files to
              the appropriate places in the file system. 
