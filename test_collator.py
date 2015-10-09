#!/usr/bin/env python3

import unittest
import os.path
from tempfile import TemporaryDirectory, TemporaryFile
from PDF_collator import system_checks, file_check

class SystemCheckTest(unittest.TestCase):
    """Class for testing system checks work in PDF_collator.py."""

    def setUp(self):
        self.corp_cocs = ['123456coc.pdf', '123456acoc.pdf', '123457coc.pdf',
                          '123460-470coc.pdf', '123980-012coc.pdf',
                          '1234coc.pdf', '400400a.pdf', 'QC123-456coc.pdf',
                          'SP12-345coc.pdf'
                         ]
        self.fail("This setUp method hasn't been created yet.")

    def checkFilesExist(self):
        with TemporaryDirectory() as tmpdir:
            # No files in dir initially
            self.assertFalse(file_check(tempfile.gettempdir()))
            # Add .DS_Store file - should still return false
            ds_loc = os.path.join(tempfile.gettempdir(), '.DS_Store')
            ds = open(ds_loc, 'w')

            # No files, despite .DS_Store
            sel.assertFalse(file_check(tempfile.gettempdir()))

            # Clean up
            ds.close()
            os.path.remove(ds)
        self.assertTrue(file_check(os.path.expanduser('~')))

    def tearDown(self):
        self.fail("This tearDown method hasn't been created yet.")


if __name__ == '__main__':
    unittest.main()
