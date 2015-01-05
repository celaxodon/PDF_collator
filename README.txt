This document notes design decisions and usage patterns for the project
entitled "Report_collator".

### PDF collating program notes ####

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




############################
### Program Requirements ###
############################

1. Strip leading "Job_" chars
2. Collect applicable CoC and move to temp folder
2.1 Human step here? Any kind of review?
3. gs script should run to rotate and combine pdfs. Should output
   (some kind of naming scheme) to a folder for renaming (manual step)
4. Should be able to handle QC/WP/SP reports as well.


#####################
###     Notes     ###
#####################

.../Files_to_strip - dir that S will put files into to eventually be
                     combined.

.../To File - Final dir that K will use in renaming and filing.

.../ToPDF - Where files are located when awaiting combination with gs
            script.

#####################
###     To Do     ###
#####################

1. optional output - input file sizes and output pdf file size + compression ratio!
