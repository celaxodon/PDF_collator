#!/usr/bin/env python3

import unittest
import os
import os.path
from tempfile import TemporaryDirectory, TemporaryFile

from PDF_collator import system_checks, file_check, name_check, strip_chars
from PDF_collator import get_ranges, total_file_size, find_coc, backcheck


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
            for f in os.listdir(self.test_dir.name):
                os.remove(os.path.join(self.test_dir.name, f))
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
        # Test it works with multiple function arguments
        self.tmpdir3 = TemporaryDirectory()
        self.tmpdir4 = TemporaryDirectory()

        # Create files in temporary directory for name testing
        for f in self.good_list + self.bad_list:
            g = open(os.path.join(self.tmpdir.name, f), 'w')
            g.close()
            
            m = open(os.path.join(self.tmpdir3.name, f), 'w')
            m.close()


        # Create only good file names in tmpdir2
        for i in self.good_list:
            j = open(os.path.join(self.tmpdir2.name, i), 'w')
            j.close()

            n = open(os.path.join(self.tmpdir4.name, i), 'w')
            n.close()


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

        self.two_args_check = name_check(self.tmpdir3.name, self.tmpdir4.name)
        self.assertEqual(s1, set(self.two_args_check))

    def tearDown(self):
        dirlist = [self.tmpdir, self.tmpdir2,
                   self.tmpdir3, self.tmpdir4]
        try:
            for d in dirlist:
                for f in os.listdir(d.name):
                    os.remove(os.path.join(d.name, f))
                if os.path.exists(d.name):
                    d.cleanup()
            
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

        # Good and bad (mixed) data
        self.mixed_name_list = ['job_123456pg1.pdf', '    123456pd1.pdf',
                                'ybb_ 123456pg1.pdf', 'job_2056 408129pg2.pdf',
                                'job_12345 408999pg21.pdf', '123456pg1.pdf']

        # Bad names from mixed_name_list
        self.mixed_bad_names = ['job_123456pg1.pdf', '    123456pd1.pdf',
                                'ybb_ 123456pg1.pdf', '408999pg21.pdf']

        # Return for good data from mixed_name_list
        self.mixed_data_result = ['408129pg2.pdf', '123456pg1.pdf']


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
        valid_data, errors = strip_chars(self.tmpdir.name)
        self.assertEqual(errors, None)
        self.assertEqual(set(os.listdir(self.tmpdir.name)), set(valid_data))

        valid_data2, errors2 = strip_chars(self.tmpdir2.name)
        self.assertEqual(set(errors2), set(self.mixed_bad_names))
        self.assertEqual(set(valid_data2), set(self.mixed_data_result))

    def testFileSize(self):
        # Don't really know how to test the return value of a function that gets
        # the size of files in a directory except by checking the type of its
        # return value...
        self.assertTrue(type(total_file_size(self.tmpdir.name)), int)

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


class ChainAnalysis(unittest.TestCase):

    def setUp(self):
        # Testing normal, normal range, normal range lacking matching pdfs,
        # QC chains, single rerun samples, range rerun samples.

        # Should have clean data by this point!
        # Test data for backcheck function
        self.backcheck_cocs = ['123456coc.pdf', '123457-460coc.pdf',
                               '123461-463coc.pdf', '123000acoc.pdf',
                               '123001a-004acoc.pdf']

        # Note 123461-463coc.pdf - won't have all the matching pdfs
        self.incomplete_pdfs = ['123456pg1.pdf', '123457pg2.pdf', '123458pg1.pdf', 
                              '123459pg1.pdf', '123460pg1.pdf', '123462pg1.pdf',
                              '123463pg2.pdf', 'QC123-345pg1.pdf', '123000apg2.pdf',
                              '123001apg2.pdf', '123002apg1.pdf', '123003apg1.pdf']

        self.complete_pdfs = ['123456pg1.pdf', '123457pg2.pdf', '123458pg1.pdf', 
                              '123459pg1.pdf', '123460pg1.pdf', '123461pg1.pdf',
                              '123462pg1.pdf', '123463pg2.pdf', 'QC123-345pg1.pdf',
                              '123000apg2.pdf', '123001apg2.pdf', '123002apg1.pdf',
                              '123003apg1.pdf', '123004apg2.pdf']

        # Test data for get_ranges function
        self.range_sample = '123456-460coc.pdf'
        self.range_rerun1 = '123456a-460acoc.pdf'
        self.range_rerun2 = '123997b-002bcoc.pdf'
        self.qc_sample = 'QC123-456coc.pdf'
        self.wp_sample = 'WP123-456coc.pdf'

        self.range_return = ['123456', '123457', '123458', '123459', '123460']

        self.rerun1_result = ['123456a', '123457a', '123458a', '123459a',
                             '123460a']

        self.rerun2_result = ['123997b', '123998b', '123999b', '124000b',
                             '124001b', '124002b']
        self.qc_return = ['QC123-456']
        self.wp_return = ['WP123-456']


    def test_get_ranges_fn(self):
        self.assertEqual(get_ranges(self.range_sample), set(self.range_return))
        self.assertEqual(get_ranges(self.range_rerun1), set(self.rerun1_result))
        self.assertEqual(get_ranges(self.range_rerun2), set(self.rerun2_result))
        self.assertEqual(get_ranges(self.qc_sample), set(self.qc_return))
        self.assertEqual(get_ranges(self.wp_sample), set(self.wp_return))

    def test_backcheck_fn(self):
        for f in self.backcheck_cocs:
            # All pdfs found based on CoC name - only check errors returned
            self.assertEqual(backcheck(f, self.complete_pdfs)[1], None)

        # Test for incomplete pdfs as indicated by coc range
        required_pdfs1, errors1 = backcheck('123461-463coc.pdf', self.incomplete_pdfs)
        self.assertEqual(set(required_pdfs1), set(['123461', '123462', '123463']))
        self.assertEqual(errors1, ['123461'])

        required_pdfs2, errors2 = backcheck('123001a-004acoc.pdf', self.incomplete_pdfs)
        self.assertEqual(set(required_pdfs2), set(['123001a', '123002a', '123003a', '123004a']))
        self.assertEqual(errors2, ['123004a'])


class ChainCollection(unittest.TestCase):

    def setUp(self):
        A_set = []
        C_set = []
        P_set = ['QC123-456coc.pdf', 'WP123-456coc.pdf', 'WP123-456acoc.pdf',
                 'SP123-456coc.pdf']
        self.coc_list = []
        self.clean_pdfs = ['123456pg1.pdf', '123457pg2.pdf', '123458pg1.pdf', 
                           '123459pg1.pdf', '123460pg1.pdf', '123461pg1.pdf',
                           '123462pg1.pdf', '123463pg2.pdf', 'QC123-456pg1.pdf',
                           'QC123-456pg2.pdf', 'WP123-456pg1.pdf', 'WP123-456pg2.pdf',

                           '123000apg2.pdf', '123001apg2.pdf', '123002apg1.pdf',
                           '123003apg1.pdf', '123004apg2.pdf']

    def test_find_coc_fn(self):
        self.fail("The test for testing CoC collection hasn't been written yet.")

    def test_aggregator_fn(self):
        self.fail("The test for testing the aggregator function hasn't been written yet.")


if __name__ == '__main__':
    unittest.main()
