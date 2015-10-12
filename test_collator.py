#!/usr/bin/env python3

import unittest
import os.path
from tempfile import TemporaryDirectory, TemporaryFile
from PDF_collator import system_checks, file_check, name_check

class SystemCheckTest(unittest.TestCase):
    """Class for testing system checks work in PDF_collator.py."""

    def setUp(self):
        self.test_dir = TemporaryDirectory()

    def testFilesExist(self):
        # No files in dir initially
        self.assertFalse(file_check(self.test_dir.name))
        # Create temporary .DS_Store file
        DS_file = open(os.path.join(self.test_dir.name, '.DS_Store'), 'w')
        DS_file.close()
        # No files, despite .DS_Store
        self.assertFalse(file_check(self.test_dir.name))

        self.assertTrue(file_check(os.path.expanduser('~')))

    def tearDown(self):
        # Clean up temp dir/file
        # May be unnecessary with TemporaryDirectory() handling.
        try:
            os.remove(os.path.join(self.test_dir.name, '.DS_Store'))
            os.rmdir(self.test_dir.name)
        except OSError:
            print("There was an error removing the temporary directory and "
                  "test .DS_Store file from the SystemCheckTest test suite.")
            print("Error was {0}".format(OSError))


class NameChecks(unittest.TestCase):
    """Class for testing name checking function in PDF_collator.
    
    Valid naming schemes are as follows:

        123456coc.pdf           -- Single CoCs
        123456-460coc.pdf       -- Range CoCs
        123456acoc.pdf          -- Single rerun CoCs
        123456a-460acoc.pdf     -- Range rerun CoCs
        QC123-456coc.pdf        -- QC/SP/WP sample CoCs
    """

    def setUp(self):
        self.good_list = ['123456coc.pdf', '123456acoc.pdf', 'QC123-456coc.pdf',
                          '123450-470coc.pdf', '123980-012coc.pdf']
        self.bad_list = ['444999.pdf', '400400a.pdf', 'SP12-345coc.pdf',
                         '123400coc-123401coc.pdf', '123459-420coc.pdf',
                         '123456cpc.pdf', '123456coc', '.DS_Store']
        # What about repeat files? Or two reports that need the same COC?
        self.tmpdir = TemporaryDirectory()
        self.tmpdir2 = TemporaryDirectory()

        # Create files in temporary directory for name testing
        for f in self.good_list + self.bad_list:
            g = open(os.path.join(self.tmpdir.name, f), 'w')
            g.close()

        # Create only good file names in tmpdir2
        for i in self.good_list:
            j = open(os.path.join(self.tmpdir2.name, i), 'w')
            j.close()

    def testFileNames(self):
        self.returned_list = name_check(self.tmpdir.name)
        self.new_bad_list = self.bad_list
        self.new_bad_list.remove('.DS_Store')
        self.assertEqual(self.new_bad_list, self.returned_list)

        self.valid_return= name_check(self.tmpdir2.name)
        self.assertEqual(self.valid_return, None)

    def tearDown(self):
        try:
            for f in os.listdir(self.tmpdir.name):
                os.remove(os.path.join(self.tmpdir.name, f))
            os.rmdir(self.tmpdir.name)
            
            for i in os.listdir(self.tmpdir2.name):
                os.remove(os.path.join(self.tmpdir2.name, i))
            os.rmdir(self.tmpdir2.name)

        except OSError:
            print("There was an error removing the temporary files and "
                  "directories from the NameChecks test suite.")


if __name__ == '__main__':
    unittest.main()
