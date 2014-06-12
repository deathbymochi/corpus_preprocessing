"""Tests for the trigrams module"""

import sys, os
sys.path.insert(0, os.path.abspath(__file__ + "/../../"))
import unittest
from corpus_preprocessing.core import trigrams as mod_ut

class TestStringToWordListFunction(unittest.TestCase):
    """Tests string_to_words_list function turns string into
    word list properly
    """
    def setUp(self):
    	"""Defines things used in testing"""
    	self.string_oneword = "oneword"
    	self.words_oneword = [("oneword", 0)]
    	self.string_1 = "this is a string"
    	self.words_1 = [('this', 0), ('is', 1), ('a', 2), ('string', 3)]
    	self.string_2 = "this string's got an apostrophe"
    	self.words_2 = [('this', 0), ("string's", 1), ('got', 2),
    	    ('an', 3), ('apostrophe', 4)]
    	self.string_3 = "this|is|a|transcript"
    	self.words_3 = [('this', 0), ('is', 1), ('a', 2), ('transcript', 3)]

    def test_simple_single_word_to_wordlist(self):
    	"""Tests that string made of a single word is converted to
    	word list of single word"""
    	obj_ut = mod_ut.string_to_words_list(self.string_oneword)
    	self.assertEqual(obj_ut, self.words_oneword)

    def test_simple_string_to_wordlist(self):
    	"""Tests that simple string is converted to word list"""
    	obj_ut = mod_ut.string_to_words_list(self.string_1)
    	self.assertEqual(obj_ut, self.words_1)

    def test_simple_punct_string_to_wordlist(self):
    	"""Tests that by default, string w/ punctuation is only split on spaces
    	when converted"""
    	obj_ut = mod_ut.string_to_words_list(self.string_2)
    	self.assertEqual(obj_ut, self.words_2)

    def test_bar_string_to_wordlist(self):
    	"""Tests that when delimiter is '|', string is separated by '|'"""
    	obj_ut = mod_ut.string_to_words_list(self.string_3, '|')
    	self.assertEqual(obj_ut, self.words_3)

class TestRemoveBadWordsFunction(unittest.TestCase):
    """Tests remove_bad_words function removes bad words properly"""
    def setUp(self):
    	"""Define things used in testing"""
    	self.words_simple = [('most', 0), ('cats', 1), ('sleep', 2),
    	('during', 3), ('the', 4), ('day', 5), ('in', 6), ('China', 7),
    	('and', 8), ('Egypt', 9)]
    	self.words_allbad = [('the', 0), ('the', 1), ('and', 2), ('in', 3)]

    	self.bad_zero = []
    	self.bad_simple = ['the', 'in', 'and']

    	self.new_words_simple = [('most', 0), ('cats', 1), ('sleep', 2),
    	('during', 3), ('day', 5), ('China', 7), ('Egypt', 9)]
    	self.new_words_allbad = []

    def test_removes_nothing_when_nobad(self):
    	"""Tests that func doesn't remove anything when no
    	bad words in bad words list
    	"""
    	obj_ut = mod_ut.remove_bad_words(self.words_simple, self.bad_zero,
    		"remove")
    	self.assertEqual(obj_ut, self.words_simple)

    def test_removes_bad_words_simple(self):
    	"""Tests that func removes bad words correctly from simple wordlist"""
    	obj_ut = mod_ut.remove_bad_words(self.words_simple, self.bad_simple,
    		"remove")
    	self.assertEqual(obj_ut, self.new_words_simple)

    def test_removes_all_if_all_are_bad(self):
    	"""Tests that func removes all words from wordlist if all
    	words are bad
    	"""
    	obj_ut = mod_ut.remove_bad_words(self.words_allbad, self.bad_simple,
    		"remove")
    	self.assertEqual(obj_ut, self.new_words_allbad)

class TestMakeTrigramsFunction(unittest.TestCase):
    """Tests make_trigrams function makes trigrams properly"""
    def setUp(self):
    	"""Define things used in testing"""
    	self.words_notrigrams_1 = [('most', 0), ('like', 3)]
    	self.words_notrigrams_2 = [('most', 0), ('like', 3), ('but', 8)]
    	self.words_notrigrams_3 = [('most', 0), ('like', 3), ('but', 8),
    	    ('never', 15)]

    	self.words_simple = [('most', 0), ('cats', 1), ('sleep', 2)]
    	self.trigrams_simple = ['most', 'cats', 'sleep', 'most cats',
    	    'most - sleep', 'cats sleep']

    	self.words_longer = [('most', 0), ('cats', 1), ('sleep', 2),
    	    ('during', 3), ('the', 4), ('day', 5)]
    	self.trigrams_longer = ['most', 'cats', 'sleep', 'during', 'the',
    	    'day', 'most cats', 'most - sleep', 'cats sleep', 'cats - during',
    	    'sleep during', 'sleep - the', 'during the', 'during - day',
            'the day']

    	self.words_space_1 = [('most', 0), ('sleep', 2), ('during', 3),
    	    ('day', 5)]
    	self.trigrams_space_1 = ['most', 'sleep', 'during', 'day',
    	    'most - sleep', 'sleep during', 'during - day']
    	self.words_space_2 = [('most', 0), ('sleep', 3),
            ('during', 4), ('next', 6), ('day', 7)]
    	self.trigrams_space_2 = ['most', 'sleep', 'during', 'next', 'day',
    	    'sleep during', 'during - next', 'next day']

    def test_trigrams_none(self):
    	"""Tests that func returns only unigrams when no possible
        multigrams can be made from word list
    	"""
    	obj_ut1 = mod_ut.make_trigrams(self.words_notrigrams_1)
    	self.assertEqual(obj_ut1, ['most', 'like'])
    	obj_ut2 = mod_ut.make_trigrams(self.words_notrigrams_2)
    	self.assertEqual(obj_ut2, ['most', 'like', 'but'])
    	obj_ut3 = mod_ut.make_trigrams(self.words_notrigrams_3)
    	self.assertEqual(obj_ut3, ['most', 'like', 'but', 'never'])

    def test_trigrams_simple(self):
    	"""Tests that func makes trigrams out of simple wordlist (3 words,
    	no words taken out) correctly
    	"""
    	obj_ut = mod_ut.make_trigrams(self.words_simple)
    	self.assertEqual(obj_ut, self.trigrams_simple)

    def test_trigrams_longer(self):
    	"""Tests that func makes trigrams out of longer simple wordlist
    	(>3 words, no words taken out) correctly
    	"""
    	obj_ut = mod_ut.make_trigrams(self.words_longer)
    	self.assertEqual(obj_ut, self.trigrams_longer)

    def test_trigrams_spaces(self):
    	"""Tests that func makes trigrams out of wordlist that has spaces"""
    	obj_ut1 = mod_ut.make_trigrams(self.words_space_1)
    	self.assertEqual(obj_ut1, self.trigrams_space_1)
    	obj_ut2 = mod_ut.make_trigrams(self.words_space_2)
    	self.assertEqual(obj_ut2, self.trigrams_space_2)


if __name__ == "__main__":
    unittest.main()
