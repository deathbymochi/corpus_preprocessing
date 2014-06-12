"""Tests for the core_body_func module"""

import sys,os
sys.path.insert(0, os.path.abspath(__file__ + "/../../"))
import unittest
import gensim as gs
import numpy as np
from corpus_preprocessing.core import compare_corpus as mod_ut

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
		self.merged_core1 = {'apple': [10, 1], 'cat': [5, 19]}
                self.merged_core2 = {'apple': [10, 1], 'cat': [5, 19],
		'bread': [5, 10]}

	def test_pvals_as_expected(self):
		"""Tests that ttest pvals calculated by func have approx expected
		values
		"""
		obj_ut = dict(mod_ut.df_ttest_pval_generator(self.merged_core1, 20, 40))
		self.assertTrue(obj_ut['apple'] < 0.1)
		self.assertTrue(obj_ut['cat'] < 0.1)

	def test_high_pvals_omitted(self):
		"""Tests that tokens with high pvals are omitted from results
		"""
		obj_ut = dict(mod_ut.df_ttest_pval_generator(self.merged_core2, 20, 40))
		self.assertTrue(obj_ut['apple'] < 0.1)
		self.assertTrue(obj_ut['cat'] < 0.1)
		self.assertFalse('bread' in obj_ut)


if __name__ == '__main__':
	unittest.main()
