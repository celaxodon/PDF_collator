#!/usr/bin/env python3

import unittest
import os
import os.path
from tempfile import TemporaryDirectory, TemporaryFile

from PDF_collator import system_checks, file_check, name_check, strip_chars

class SystemCheckTest(unittest.TestCase):
    """Class for testing system checks work in PDF_collator.py."""

    def setUp(self):
        self.test_dir = TemporaryDirectory()
        self.dir_list = ['Data', 'scans', 'Admin']

    def testFilesExist(self):
        # No files in dir initially
        self.assertFalse(file_check(self.test_dir.name))
        # Create temporary .DS_Store file
        DS_file = open(os.path.join(self.test_dir.name, '.DS_Store'), 'w')
        DS_file.close()

        # No files, despite .DS_Store
        self.assertFalse(file_check(self.test_dir.name))

        self.assertTrue(file_check(os.path.expanduser('~')))

    def testMountedDirectories(self):
        for d in self.dir_list:
            if os.path.exists(os.path.join('/Volumes', d)):
                self.assertTrue(system_checks())

    def tearDown(self):
        try:
            os.remove(os.path.join(self.test_dir.name, '.DS_Store'))
            if os.path.exists(self.test_dir.name):
                self.test_dir.cleanup()
                
        except OSError:
            print("There was an error removing the temporary directory and "
                  "test .DS_Store file from the SystemCheckTest test suite.")
            print("Error was {0}".format(OSError))

        except FileNotFoundError:
            print("There was an error removing the temporary directory!")


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
                          '123450-470coc.pdf', '123980-012coc.pdf',
                          '123450a-470acoc.pdf', 'QC123-345coc.pdf',
                          'SP240-012coc.pdf', 'WP242-560coc.pdf']
        self.bad_list = ['444999.pdf', '400400a.pdf', 'SP12-345coc.pdf',
                         '123400coc-123401coc.pdf', '123459-420coc.pdf',
                         '123456cpc.pdf', '123456coc', '.DS_Store',
                         '123500-500coc.pdf', '123456a-123460coc.pdf',
                         '123456-123460acoc.pdf', '123400-390coc.pdf',
                         'QP123-345coc.pdf', 'WP123-34coc.pdf']

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
        # Using sets b/c lists don't return same order.
        s1 = set(self.new_bad_list)
        s2 = set(self.returned_list)
        self.assertEqual(s1, s2)

        self.valid_return = name_check(self.tmpdir2.name)
        self.assertEqual(self.valid_return, None)

    def tearDown(self):
        try:
            for f in os.listdir(self.tmpdir.name):
                os.remove(os.path.join(self.tmpdir.name, f))
            if os.path.exists(self.tmpdir.name):
                self.tmpdir.cleanup()
            
            for i in os.listdir(self.tmpdir2.name):
                os.remove(os.path.join(self.tmpdir2.name, i))
            if os.path.exists(self.tmpdir2.name):
                self.tmpdir2.cleanup()

        except OSError:
            print("There was an error removing the temporary files and "
                  "directories from the NameChecks test suite.")

        except FileNotFoundError:
            print("There was an error removing the temporary directory!")


class NameStripper(unittest.TestCase):
    """Class for testing strip_chars function in PDF_collator.py."""

    def setUp(self):
        self.valid_name_list = ['job_2055 408129pg1.pdf',
                'job_2056 408129pg2.pdf', 'job_20579 408129pg3.pdf',
                'job_205899 560044pg1.pdf', 'job_205 560044pg2.pdf',
                'job_206 560044pg3.pdf', 'job_20 560045pg1.pdf',
                'job_19 560045pg2.pdf', 'job_2 560045pg3.pdf',
                'job_2 560046pg1.pdf', 'job_20651 560046pg2.pdf',
                'job_20661 560046pg3.pdf',
                ]
        # Result of os.listdir
        self.valid_result = ['408129pg1.pdf', '560046pg3.pdf',
                             '408129pg2.pdf', '408129pg3.pdf',
                             '560044pg1.pdf', '560044pg2.pdf',
                             '560044pg3.pdf', '560045pg1.pdf',
                             '560045pg2.pdf', '560045pg3.pdf',
                             '560046pg1.pdf', '560046pg2.pdf',
                             ]

        self.mixed_name_list = ['job_123456pg1.pdf', '    123456pd1.pdf',
                                'ybb_ 123456pg1.pdf', 'job_2056 408129pg2.pdf',
                                'job_12345 408999pg21.pdf']
        # Result of os.listdir after strip_chars on mixed_name_list dir
        self.mixed_data_result = ['job_123456pg1.pdf', '    123456pd1.pdf',
                                  'ybb_ 123456pg1.pdf', '408129pg2.pdf',
                                  '408999pg21.pdf']
        # Return value for strip_chars from mixed_name_list
        self.mixed_bad_names = ['job_123456pg1.pdf', '    123456pd1.pdf',
                                'ybb_ 123456pg1.pdf', '408999pg21.pdf']


        # Set up temp folders for data tests
        self.tmpdir = TemporaryDirectory()
        # populate with valid data
        for item in self.valid_name_list:
            f = open(os.path.join(self.tmpdir.name, item), 'w')
            f.close()

        self.tmpdir2 = TemporaryDirectory()
        # Populate with invalid data
        for item in self.mixed_name_list:
            f = open(os.path.join(self.tmpdir2.name, item), 'w')
            f.close()

    def testCharacterStripper(self):
        valid_data = strip_chars(self.tmpdir.name)
        self.assertEqual(valid_data, None)
        s1 = set(os.listdir(self.tmpdir.name))
        s2 = set(self.valid_result)
        self.assertEqual(s1, s2)

        bad_data = set(strip_chars(self.tmpdir2.name))
        s3 = set(self.mixed_bad_names)
        self.assertEqual(bad_data, s3)
        s4 = set(os.listdir(self.tmpdir2.name))
        s5 = set(self.mixed_data_result)
        self.assertEqual(s4, s5)

    def tearDown(self):
        try:
            for f in os.listdir(self.tmpdir.name):
                os.remove(os.path.join(self.tmpdir.name, f))
            if os.path.exists(self.tmpdir.name):
                self.tmpdir.cleanup()

            for g in os.listdir(self.tmpdir2.name):
                os.remove(os.path.join(self.tmpdir2.name, g))
            if os.path.exists(self.tmpdir2.name):
                self.tmpdir2.cleanup()
            
        except OSError:
            print("There was an error removing the temporary files and "
                  "directories from the NameStripper test suite.")
        except FileNotFoundError:
            print("There was an error removing the temporary directory!")


class ChainCollection(unittest.TestCase):

    def setUp(self):
        pass
    def testMappings(self):
        self.fail("The test for testing CoC mappings hasn't been written yet.")
        pass
    def tearDown(self):
        pass


if __name__ == '__main__':
    unittest.main()
