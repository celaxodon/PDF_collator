=============
PDF\_collator
=============

The PDF_collator program was designed to programmatically locate, organize and
collate PDF files with numerical naming schemes. Created as a stopgap measure
to augment the lack of PDF collating and printing in a Laboratory Information
Management System (LIMS), the script gradually grew too far and fast to
be easily maintained as a shell script. 

This Python version is a rewrite meant make maintenance and readability easier.

Features
--------

As of June, 2015, the script has been designed to do the following:

* Checks that necessary filesystems have been mounted.

* Searches for and collects Chain of Custody (COC) PDFs, which
  will match numerically with various LIMS-produced PDFs.

* Checks that the full range of files, as indicated by the COC naming scheme.
  If the full range is not found, a warning is given to the user, but proceeds
  with the collation anyway

* Performs some basic error checking on COC files. This is complemented by a
  cron job, which is run daily on the file server, to ensure accurate naming.

* Creates temporarary directories, reorders COC PDFs and report files first.

* Uses Ghostscript to collate reports and reduce their final size.

  **Note**: This needs to be revisited. In testing, ghostscript was more efficient
  at reducing overall PDF file size than pypdf2, but slightly less efficient 
  than Adobe's software. 

* Disposes of filees after collation, and moves reports to appropriate location.

* Has a reset function to clean up the temporary directory files. This will
  return files to their original location, based on filename. Only needs to 
  be used in the event that COC files are improperly named. 

Note: Better error handling is needed. 


To do:
------

- logging (?)
- error handling
- CoC collection and collation
- Compression stats

Design Notes
------------

Ghostscript was chosen as an alternative to the previous solution, which used
an Apple script. The apple script, part of Apple's automator software, used 
pypdf2 and was inefficient at reducing PDF size. Ghostscript also holds the 
advantage of being able to rotate PDFs automatically. 

For refering to the Applescript Automator's PDF script, see
`/System/Library/Automator/Combine PDF Pages.action/Contents/Resources/join.py`

At times, using this script caused collated PDFs to _balloon_ in size instead
of shrink. 

**_Ghostscript usage_**

Ghostscript is fast and accurate, but doesn't take input well. 
Both piping input into GS and an array with PDF titles were attempted, 
but both failed.  So far, the only syntax gs recognizes for multiple pdf inputs
is to either list them, as so:

`<gs script here> pdf1.pdf pdf2.pdf ...`

or

`<gs script> files*pdf`

Furthermore, output locations don't seem to be able to be specified, though 
that needs to be checked. 

Usage
-----

PDF_collator [OPTIONS] Collates reviewed data PDFs with their matching Chain of 
                       Custody files. Final reports are filed for both billing
                       and delivery to clients. 

OPTIONS:
  -h, --help Prints the usage guide

  -r, --reset Resets pdfs and their associated Chain of Custody (CoC) files to
              the appropriate places in the file system. 



Python Rewrite
--------------

Considerations:
  * What's the best way to compress?
  * Get file operations down to functions, then worry about compression
  * Think about algorithm for finding PDFs and CoCs and matching
    A. Look to PDF numbers, find CoCs accordingly. This is close to the previous
       implementation where we generated a range of PDF numbers, and matched
       each one with a COC, moving the COC to its own "$last_tmp" folder. 
       The folder had the last number the COC covered in its range. All
       PDFs and the appropriate COC were then moved to that folder for
       collation. 
    B. Look to COCs, generate ranges they encompass, match with PDFs. Do it
       with dictionaries. Delete any keys that don't have PDFs associated.
       This method could use sets for quick membership checking
    
Possible PDF packages:
----------------------

* PDF 1.0
* PDFTron-PDFNet_SDK-for-Python 5.7
* pdfminer3k
* pdfrecycle
* pdfsplit
* pdftools.pdfjoin
* pdfcat
* py-pdf-collate
* PyPDF2
* Ghostscript -- the python package in pypi is Linux and Python 2.x compatible only.
                 Could port, but look at other functionality first.
