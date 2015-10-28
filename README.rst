=============
PDF\_collator
=============

The PDF_collator program was designed to programmatically locate, organize and
collate PDF files with numerical naming schemes. Created as a stopgap measure
to augment the lack of PDF collating and printing in a Laboratory Information
Management System (LIMS), the script gradually grew too far and fast to
be easily maintained as a shell script. 

This Python rewrite is intended to make the code easier to maintain and
understand, and to improve the performance and error handling.

Features
--------

As of June, 2015, the script has been designed to do the following:

* Checks that necessary filesystems have been mounted.

* Checks that the full range of files, as indicated by the COC naming scheme.
  If the full range is not found, a warning is given to the user, but proceeds
  with the collation anyway

* Searches for and collects Chain of Custody (COC) PDFs, which
  will match numerically with various LIMS-produced PDFs.

* Performs some error checking (by regex) on COC and PDF files.

* Creates temporarary directories, reorders COC PDFs and report files first.

* Uses Ghostscript to collate reports and reduce their final size.

  **Note**: This needs to be revisited. In testing, ghostscript was more efficient
  at reducing overall PDF file size than pypdf2, but slightly less efficient 
  than Adobe's software. Testing of additional gs options below is needed to
  enhance compression. 

* Disposes of files after collation, and moves reports to appropriate location.

* Has a reset function to clean up the temporary directory files. This will
  return files to their original location, based on filename. Only needs to 
  be used in the event that COC files are improperly named. 


To do:
------

- logging (?)

- error handling

- CoC collection and collation

- Compression stats

  - Function should take a file and return its size (KB/MB/GB) -- both of the
    below return size in bytes
  - os.path.getsize() -- uses os.stat
  - os.stat way -- instatiate, then call st_size attribute

- Concatenation/compression options:
  - Use a subprocess (std lib) - see: http://stackoverflow.com/questions/27631940/python-script-to-compress-all-pdf-files-in-a-directory-on-windows-7
  - Use a system call to `gs` (std lib)

- Install script or function to download if current version not on host. 

    - See _pages.uoregon.edu/koch/Ghostscript-9.16.pkg

- Testing
  - [DONE] backcheck function
  - [DONE] get_range function

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

* NOTE: Double check that output file locations can be specified.

* Script from Bash version of PDF_collator:

  `gs -dBATCH -dNOPAUSE -q -sDEVICE=pdfwrite -dAutoRotatePages=/PageByPage -sOutputFile="$FILENAME" ./*.pdf 2>/dev/null;`

  - `-dBATCH` -- Exit after last file, rather than going into an interactive
    reading postscript commands.

  - `-dNOPAUSE` -- No pause after page.

  - `-o` -- Implies `-dBATCH` and `-dNOPAUSE`.

  - `-q` -- Quiet mode; suppress messages.

  - `-sDEVICE=pdfwrite` -- Selects the output device ghostscript should use.
    Here, the output device is a pdfwriter.

  - `-dAutoRotatePages=/PageByPage` --

  - `-sOutputFile=$FILENAME` -- Designate a file name to write to

The following options are experimental and compression-related:

  - `-dEmbedAllFonts=true` -- Ensures that the fonts you used in creating
    the pdf are used by whomever views the pdf. A full copy of the entire
    charset is embedded (INCREASES SIZE)
  - `-dSubsetFonts=false` -- This option will embed a subset of the font
    character sets in your pdf - only the characters that are displayed in
    the PDF, though.
  - `-dPDFSETTINGS=/screen` -- screen-view quality only (72 dpi)
        `/ebook` -- low quality (150 dpi images)
        `/printer` -- high quality (300 dpi images)
        `/prepress` -- high quality (300 dpi images, preserves colors)
        `/default` -- almost the same as /screen.
  - `-dOPTIMIZE=true` -- 
  - `-dCompatibilityLevel=x.x` -- Adobe's PDF specification...
    - `1.4` -- for font embedding
    - `1.6` -- for OpenType font embedding
  - `-dAutoFilterColorImages=false` --
  - `-dColorImageFilter=/FlateEncode` -- lossless compression?

Usage
-----

`PDF_collator.py [OPTIONS]` -- Collates reviewed data PDFs with their matching
Chain of Custody files. Final reports are filed for both billing and delivery
to clients. 

OPTIONS:
  `-h`, `--help` -- Prints the usage guide

  `-r`, `--reset` -- Resets pdfs and their associated Chain of Custody (CoC)
  files to the appropriate places in the file system. 


Python Rewrite
--------------

Considerations:
  * What's the best way to compress? 
    * Ghostscript, hands down
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
    
* PyPDF2 - can merge and write pdfs (lots of pdf manipulation options). gs
  is the tool we need here, though, because of compression. 
* Ghostscript -- the python package in pypi is Linux and Python 2.x compatible only.
  * Could port/fork, but look at other functionality first.
