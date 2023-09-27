#!/usr/bin/env python3

"""Template/boilerplate for writing new test classes"""

# Note this will get discovered and run as a no-op test. This is fine.

import sys, os, re
import unittest
import logging
from unittest.mock import Mock, patch # if needed

VERBOSE = os.environ.get('VERBOSE', '0') != '0'

from transfer_test_maker import ( pad_filename,
                                  gen_names )


class T(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        #Prevent the logger from printing messages - I like my tests to look pretty.
        if VERBOSE:
            logging.getLogger().setLevel(logging.DEBUG)
        else:
            logging.getLogger().setLevel(logging.CRITICAL)

    def setUp(self):
        # See the errors in all their glory
        self.maxDiff = None

    ### THE TESTS ###
    def test_pad_filename(self):

        res1 = pad_filename("foo", minlen=14, pad="paPA", extn=".bar")
        self.assertEqual(res1, "foo_paPApa.bar")

        res2 = pad_filename("foo", minlen=7, pad="paPA", extn=".bar")
        self.assertEqual(res2, "foo.bar")

        res3 = pad_filename("foo", minlen=8, pad="paPA", extn=".bar")
        self.assertEqual(res3, "foo.bar")

        res4 = pad_filename("foo", minlen=9, pad="paPA", extn=".bar")
        self.assertEqual(res4, "foo_p.bar")

    def test_gen_names(self):

        # gen_names(fnum, fsize, pad_len, path_depth, file_extn)

        some_names = list( gen_names( 2, 'XXX', 0, 0, '' ) )
        self.assertEqual( some_names,
                          ['size_XXX_files_2/size_XXX_0000',
                           'size_XXX_files_2/size_XXX_0001'] )

        some_names = list( gen_names( 2, 'XXX', 0, 2, '' ) )
        self.assertEqual( some_names,
                          ['size_XXX_files_2/subdir_1/size_XXX_0000',
                           'size_XXX_files_2/subdir_1/size_XXX_0001'] )

if __name__ == '__main__':
    unittest.main()
