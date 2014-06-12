"""Tests for the core_body_func module"""

import sys,os
sys.path.insert(0, os.path.abspath(__file__ + "/../../"))
import unittest
from mockito import when
import __builtin__
import StringIO
import gensim as gs
import numpy as np
from corpus_preprocessing.core import compare_corpus as mod_ut

def set_mock_open(string_of_fo):
	fake_fo = StringIO.StringIO(string_of_fo)
	when(__builtin__).open(string_of_fo).thenReturn(fake_fo)

class TestGetToken2dfFunc(unittest.TestCase):
	"""Tests get_token2df function operates correctly"""
	def setUp(self):
		"""Defines things used in testing"""
		self.gs_dict = gs.corpora.Dictionary([
			['a', 'black', 'cat'],
			['three', 'black', 'cats'],
			['a', 'cat']])
		self.token2df = {'a': 2, 'black': 2, 'cat': 2,
		                'cats': 1, 'three': 1}

	def test_token2df(self):
		"""Tests that func creates dictionary of tokens to dfs"""
		obj_ut = mod_ut.get_token2df(self.gs_dict)
		self.assertEqual(obj_ut, self.token2df)


class TestMergeTwoCoresFunc(unittest.TestCase):
	"""Tests that merge_two_cores function operates correctly"""
	def setUp(self):
		"""Defines things used for testing"""
		self.gs_dict1 = gs.corpora.Dictionary([
			['a', 'black', 'cat'],
			['three', 'black', 'cats'],
			['a', 'cat']])
		self.gs_dict2 = gs.corpora.Dictionary([
			['a', 'black', 'cat'],
			['two', 'black', 'cats'],
			['a', 'dog']])
		self.merged_core_inner = {'a': [2, 2], 'black': [2, 2],
	                             'cat': [2, 1], 'cats': [1, 1]}
		self.merged_core_outer = dict(self.merged_core_inner.items() +
	    	                     [('three', [1, 0]), ('two', [0, 1]),
	    	                     ('dog', [0, 1])])
		self.merged_core_left = dict(self.merged_core_inner.items() +
        	                    [('three', [1, 0])])
		self.merged_core_right = dict(self.merged_core_inner.items() +
        	                     [('two', [0, 1]), ('dog', [0, 1])])

	def test_merge_cores_inner(self):
		"""Tests that func inner merges correctly"""
		obj_ut = mod_ut.merge_two_cores(self.gs_dict1, self.gs_dict2, 'inner')
		self.assertEqual(obj_ut, self.merged_core_inner)

	def test_merge_cores_outer(self):
		"""Tests that func outer merges correctly"""
		obj_ut = mod_ut.merge_two_cores(self.gs_dict1, self.gs_dict2, 'outer')
		self.assertEqual(obj_ut, self.merged_core_outer)

	def test_merge_cores_left(self):
		"""Tests that func left merges correctly"""
		obj_ut = mod_ut.merge_two_cores(self.gs_dict1, self.gs_dict2, 'left')
		self.assertEqual(obj_ut, self.merged_core_left)

	def test_merge_cores_right(self):
		"""Tests that func right merges correctly"""
		obj_ut = mod_ut.merge_two_cores(self.gs_dict1, self.gs_dict2, 'right')
		self.assertEqual(obj_ut, self.merged_core_right)


class TestMakeBinaryArrayFunc(unittest.TestCase):
	"""Tests make_binary_array func operates correctly"""
	def setUp(self):
		"""Defines things used for testing"""
		self.vec1 = [1, 1, 0, 0, 0]

	def test_make_array1(self):
		"""Tests that func makes array correctly"""
		obj_ut = mod_ut.make_binary_array(2, 5)
		self.assertEqual(list(obj_ut), self.vec1)


class TestDfTtestPvalGeneratorFunc(unittest.TestCase):
	"""Tests df_ttest_pval_generator func operates correctly"""
	def setUp(self):
		"""Defines things used in testing"""
		self.merged_core = {'apple': [10, 1], 'cat': [5, 19],
		'bread': [5, 10]}

	def test_pvals_as_expected(self):
		"""Tests that ttest pvals calculated by func have approx expected
		values
		"""
		obj_ut = dict(mod_ut.df_ttest_pval_generator(self.merged_core, 20, 40))
		self.assertTrue(obj_ut['apple'] < 0.1)
		self.assertTrue(obj_ut['cat'] < 0.1)
		self.assertTrue(obj_ut['bread'] > 0.5)


class TestWriteDfTtestToFileFunc(unittest.TestCase):
	"""Tests that write_df_ttest_to_file func operates correctly"""
	def setUp(self):
		"""Defines things used in testing"""
		self.merged_core = {'apple': [10, 1], 'cat': [5, 19],
		'bread': [5, 10]}
		self.file_result = 'bread\t1.000\napple\t0.000\ncat\t0.097\n'

	def test_writes_results_to_file(self):
		"""Tests that func writes results to file properly"""
		result = StringIO.StringIO()
		obj_ut = mod_ut.write_df_ttest_to_file(
			self.merged_core, 20, 40, handle=result)
		result.seek(0)
		self.assertEqual(result.read(), self.file_result)


class TestWordsBelowPvalGenerator(unittest.TestCase):
	"""Tests that words_below_pval_generator func operates correctly"""
	def setUp(self):
		"""Defines things used in testing"""
		self.pval_data = 'bread\t1.000\napple\t0.000\ncat\t0.097\n'
		self.words_all = ['bread', 'apple', 'cat']
		set_mock_open(self.pval_data)

	def test_pval_threshold_1(self):
		"""Tests that func keeps words whose pvals are below 1.0"""
		obj_ut = list(mod_ut.words_below_pval_generator(self.pval_data, 1))
		self.assertEqual(obj_ut, self.words_all)


if __name__ == '__main__':
	unittest.main()
