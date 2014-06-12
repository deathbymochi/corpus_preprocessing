## Functions for comparing two corpuses with each other

import gensim as gs
import numpy as np
import math
import codecs
from scipy.stats import ttest_ind
import logging

MOD_LOGGER = logging.getLogger('text_processing.compare')

def get_token2df(gs_dict):
	""" Takes a gensim Dictionary object and returns
	a normal dictionary of {token: df}

	Inputs:
	- gs_dict = gensim Dictionary object
	"""
	return {word: gs_dict.dfs[word_id] for (word_id, word) in gs_dict.items()}

def merge_two_cores(gs_dict_1, gs_dict_2, join='outer'):
    """ Takes two gensim Dictionary objects and merges them
	into a single normal dictionary of
	{token: [df in gs_dict_1, df in gs_dict_2]}

	Inputs:
	- gs_dict_1, gs_dict_2 = gensim Dictionary objects
	- join = how you want to join the tokens: 'inner' gives back only
	  tokens that are common between the two; 'outer' gives back all
	  tokens in both cores; 'left' joins on gs_dict_1; 'right' joins
	  on gs_dict_2
    """
    core_1 = get_token2df(gs_dict_1)
    core_2 = get_token2df(gs_dict_2)

    MOD_LOGGER.info('Received call to "merge_two_cores"')
    MOD_LOGGER.info(
        'Merging two cores of lengths %s and %s with %s join',
        len(core_1), len(core_2), join)

    if join == 'outer':
		tokens_set = set(core_1.keys() + core_2.keys())
    elif join == 'inner':
		tokens_set = set(token for token in core_1 if token in core_2)
    elif join == 'left':
		tokens_set = set(core_1)
    elif join == 'right':
		tokens_set = set(core_2)

    merged_core = {
        token: [core_1.get(token, 0), core_2.get(token, 0)]
        for token in tokens_set
    }

    return merged_core

def make_binary_array(num_ones, total_length):
    """ Makes a vector (aka numpy array) of 1's and 0's, where vector is
    first populated by desired number of 1's, then the rest are 0's

    Inputs:
    - num_ones = number of 1's you want
    - total_length = total length of vector
    """
    MOD_LOGGER.debug('Making binary array of length %s with %s 1s',
        total_length, num_ones)

    return np.array(
        list(np.ones(num_ones)) +
        list(np.zeros(total_length - num_ones)))

def df_ttest_pval_generator(merged_core, size_sample1, size_sample2,
    min_num=10, min_multiplier=0, pval_threshold=1):
    """ Takes a dictionary of {word: [doc frequency in sample 1,
    doc frequency in sample 2]} and conducts t-tests on dfs for each
    word; is a generator yielding [word, ttest pvalue]

    Inputs:
    - merged_core = dictionary of words to word doc freqs in two samples
    - size_sample1 = total num docs in sample 1
    - size_sample2 = total num docs in sample 2
	- min_num = threshold that word has to hit above on at least one sample
      in order to conduct ttest (eiter df1 or df2 must be >= min_num)
    - min_multiplier = min number of times token has to occur on sample1
      OVER sample2 in order to be considered (EX: 2 = occurs at least 2x
      more often on sample1 than on sample2)
    - pval_threshold = max pval allowed for [word, pval] to be yielded for
      a particular word
    """
    MOD_LOGGER.info('Received call to "df_ttest_pval_generator"')
    MOD_LOGGER.info(
        'Conducting ttest on %s tokens, ignoring tokens with df < %s and mult < %s',
        len(merged_core), min_num, min_multiplier)

    VAL_FOR_ZERO = 0.1 # val to add on to prevent division by 0 error

    for word in merged_core:
        df_sample1 = merged_core[word][0]
        df_sample2 = merged_core[word][1]

        if (df_sample1 + df_sample2) < min_num:
            continue
        if (df_sample1 == size_sample1 and df_sample2 == size_sample2):
            continue

        scope_sample1 = ((float(merged_core[word][0]) + VAL_FOR_ZERO) /
            size_sample1)
        scope_sample2 = ((float(merged_core[word][1]) + VAL_FOR_ZERO) /
            size_sample2)
        multiplier = scope_sample1 / scope_sample2

        if multiplier < min_multiplier:
            continue
        else:
            df1_array = make_binary_array(merged_core[word][0],
                size_sample1)
            df2_array = make_binary_array(merged_core[word][1],
                size_sample2)
            _, pval = ttest_ind(df1_array, df2_array)

            if not math.isnan(pval) and pval < pval_threshold:
                yield [word, pval]

def write_df_ttest_to_file(merged_core, size_sample1, size_sample2, file_name=
    None, min_num=10, min_multiplier=0, pval_threshold=1, handle=None):
    """ Takes a dictionary of {word: [doc freq in sample 1, doc freq in sample
    2]} and writes the results of conducting t-tests on dfs for each word to
    txt file

    Inputs:
    - merged_core = dictionary of words to word doc freqs in two samples
    - size_sample1 = total num docs in sample 1
    - size_sample2 = total num docs in sample 2
    - file_name = name of file to be created
    - min_num = mininum number of docs (df1 + df2) that must contain a token
      for pval to be calculated
    - min_multiplier = min number of times token has to occur on sample1
      OVER sample2 in order to be considered (EX: 2 = occurs at least 2x
      more often on sample1 than on sample2)
    - handle = file-like object (like StringIO, for testing)
    """
    if handle is None:
        fo = open(file_name, 'w')
    else:
        fo = handle

    MOD_LOGGER.info('Conducting df ttests and writing pvals to file...')

    for [word, pval] in df_ttest_pval_generator(
        merged_core, size_sample1, size_sample2, min_num, min_multiplier,
        pval_threshold):
        fo.write('%(0)s,%(1).3f,%(2)i,%(3)i\n' % {
            '0': word, '1': pval,
            '2':merged_core[word][0], '3':merged_core[word][1]})

    if handle is None:
        fo.close()

    MOD_LOGGER.info('Pvals written to %s', file_name)

def words_below_pval_generator(file_name, pval_threshold=0.5, delimiter=',',
    encoding='utf-8'):
    """ Creates generator object on file containing each word's pvalue,
    accessing only the words whose pvalues are below a given threshold

    Inputs:
    - pval_threshold = value that pvalues must be less than or equal to in
    order to be kept in generator
    - file_name = name of file containing word and pval data; word in col 1,
    pval in col 2
    """
    MOD_LOGGER.info('Received call to "words_below_pval_generator"')
    MOD_LOGGER.info(
        'Creating generator object on %s returning tokens with pval < %s',
        file_name, pval_threshold)

    for line in open(file_name):
		if delimiter is None:
			word, pval = line.split()[:2]
		else:
			word, pval = line.split(delimiter)[:2]
        # MOD_LOGGER.debug('Line in file contains: %s',
        #    {'word': word, 'pval': pval})

		if float(pval) <= pval_threshold:
			yield word.decode(encoding)



