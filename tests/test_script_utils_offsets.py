"""Tests for offsets.py functions"""
import sys,os
sys.path.insert(0, os.path.abspath(__file__ + "/../../"))
import unittest
from corpus_preprocessing import script_utils as off

class TestGetSubsetFunc(unittest.TestCase):
    """Tests that get_subset func works properly"""
    def setUp(self):
        """Defines things used in testing"""
        self.wordlist1 = ['the', 'apple', 'was', 'large', 'and', 'juicy']
        self.indexlist1 = ['0', '1', '2', '3', '4', '5']
        self.indexlist2 = [0, 1, 2, 6, 7, 8]

    def test_default_indices(self):
        """returns same list when no indices are specified"""
        obj_ut = off.get_list_subset(self.wordlist1)
        self.assertEqual(list(obj_ut), self.wordlist1)

    def test_subset_firstfour(self):
        """returns first 4 when max = 4"""
        obj_ut = off.get_list_subset(self.wordlist1, max_index=4)
        self.assertEqual(list(obj_ut), self.wordlist1[:4])

    def test_subset_lastfour(self):
        """returns last 4 (of list with len 6) when min = 2"""
        obj_ut = off.get_list_subset(self.wordlist1, min_index=2)
        self.assertEqual(list(obj_ut), self.wordlist1[2:])

    def test_neg_minindex1(self):
        """returns last 4 (of list with len 6) if min = -4, no indices"""
        obj_ut = off.get_list_subset(self.wordlist1, min_index=-4)
        self.assertEqual(list(obj_ut), self.wordlist1[2:])

    def test_neg_minindex2(self):
        """returns elements within 'last 2' index units if min = -2,
        with indices
        """
        obj_ut = off.get_list_subset(self.wordlist1, self.indexlist2,
            min_index=-4)
        self.assertEqual(list(obj_ut), self.wordlist1[3:])

if __name__ == '__main__':
    unittest.main()
