This document notes design decisions and usage patterns for the project
entitled "Report_collator".

### PDF collating program notes ####

    Ghostscript was chosen as an alternative to the current Apple script. The issue it has (somewhat) successfully addressed is file size and 
rotation of PDFs, where the Apple script fails on both.
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

