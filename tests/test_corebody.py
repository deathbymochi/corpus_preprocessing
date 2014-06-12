"""Tests for the core_body_func module"""

import sys,os
sys.path.insert(0, os.path.abspath(__file__ + "/../../"))
import unittest
from mockito import when, mock
import __builtin__
import codecs
import StringIO
from corpus_preprocessing.core import corebody as mod_ut

def fake_fo(string_of_fo):
	return StringIO.StringIO(string_of_fo)

def set_mock_open(string_of_fo):
	when(__builtin__).open(string_of_fo).thenReturn(
		fake_fo(string_of_fo))

def set_mock_codecs_open(string_of_fo):
	when(codecs).open(string_of_fo).thenReturn(
		fake_fo(string_of_fo))

class TestRawCorpusClass(unittest.TestCase):
	"""Tests RawCorpus class is instantiated and functions properly"""
	def setUp(self):
		"""Defines things used in testing"""
		self.data_noids = 'an|apple|a|day\nthree|apples|a|week\n \
		                  doctors|stay|away\n'
		self.corpus_noids = [
		    [None, ['an', 'apple', 'a', 'day']],
		    [None, ['three', 'apples', 'a', 'week']],
		    [None, ['doctors', 'stay', 'away']]]

		self.data_withids = '1\tan|apple|a|day\n2\tthree|apples|a|week\n \
		                    3\tdoctors|stay|away\n'
		self.corpus_noids = [
		    [1, ['an', 'apple', 'a', 'day']],
		    [2, ['three', 'apples', 'a', 'week']],
		    [3, ['doctors', 'stay', 'away']]]

		set_mock_open(self.data_noids)
		set_mock_open(self.data_withids)

		set_mock_codecs_open(self.data_noids)
		set_mock_codecs_open(self.data_withids)

	def test_instantiate_raw_corpus(self):
		"""Tests that RawCorpus instantiates correctly"""
		obj_ut = mod_ut.RawCorpus(self.data_noids)
		self.assertIsInstance(obj_ut, mod_ut.RawCorpus)

	def test_num_docs(self):
		"""Tests that RawCorpus counts num_docs correctly"""
		obj_ut1 = mod_ut.RawCorpus(self.data_noids)
		self.assertEqual(obj_ut1.num_docs, 3)
		obj_ut2 = mod_ut.RawCorpus(self.data_withids)
		self.assertEqual(obj_ut2.num_docs, 3)

if __name__ == "__main__":
	unittest.main()
