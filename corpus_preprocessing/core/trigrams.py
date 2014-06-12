""" This module contains functions for transforming bodies of 
text into lists of relevant uni-, bi-, and trigrams
"""

import codecs
import math
import sys
import logging
import corebody as core

MOD_LOGGER = logging.getLogger('text_processing.trigrams')

def get_words_list_from_file(file_name):
    """ Reads a file that lists single word/phrase in each row
    and transforms it to a python list of those words/phrases
    """
    words_list = []
    for line in open(file_name, 'r'):
    	words_list.append(line.split())
    
    return sum(words_list, [])

def string_to_words_list(string, word_sep=' '):
    """ Takes a string and transform it into a list of (word, word position)
    tuples
    
    Inputs:
    - string = a string
    - word_sep = char to split string on (default = ' ')
    """
    words_list = []
    string_split = string.split(word_sep)
    
    for i, word in enumerate(string_split):
    	words_list.append((word, i))
    
    return words_list

def remove_bad_words(words_list, other_words_list, method="keep"):
    """ Takes a list of (word, word position) tuples, and returns
    a new list of (word, word position) tuples where any word that
    matches a bad word is omitted; alternatively, keeps only words
    that match a good word
    
    Inputs:
    - words_list = list of (word, word position) tuples from a single text
    - other_words_list = list of words to compare your words_list to, to
      determine which words to keep
    - method = how other_words_list is viewed - if "keep", then
      other_words_list are good words, aka the words to keep; if "remove",
      then other_words_list are bad words, aka words to remove
    """
    def _is_bad_word(word, words_list, method):
    	""" For a word, compares it to a word list and returns True if
    	word is a bad word (method = "keep", word not in words_list; method
    	= "remove", word in words_list), returns False otherwise
        """
    	if method == "remove":
    		return word in words_list
    	else:
    		return word not in words_list
    
    new_words_list = []
    for (word, pos) in words_list:
    	if _is_bad_word(word, other_words_list, method):
    		continue
    	else:
    		new_words_list.append((word, pos))
    
    return new_words_list

def make_trigrams(words_list):
    """ Takes a list of (word, word position) tuples from a single text, and
    returns a list of uni- bi- and trigrams generated from this list of
    (word, word position) tuples
    
    Inputs:
    - words_list = list of (word, word position) tuples from a single text
    """
    # increase python's recursion limit for _check_multigrams (recurses 
    # through every word of a text)
    sys.setrecursionlimit(100000)
    
    # add unigrams to trigrams_list first
    trigrams_list = []
    for (word, _) in words_list:
    	trigrams_list.append(word)
    
    # check word positions to see if can make multigrams,
    # then add all viable multigrams to trigrams_list
    bigram = None
    trigram = None
    index_last = len(words_list) - 1

    def _check_multigrams(index_1, index_2, count=0):
        """ Compares indices (word position in text) of two
        adjacent words to see if they are valid bigrams
        or trigrams (either indexes are n and n+1, or n and
        n+2). Depending on the indices, recurses to the next
        valid starting point (iterates the indices) to check
        the next pair of words
        """
    	word_1 = words_list[min(index_1, index_last)]
    	word_2 = words_list[min(index_2, index_last)]
    
    	MOD_LOGGER.debug(
            'Iteration %s. 1st word %s at pos %s, 2nd word %s at pos %s.',
            count, word_1[0], word_1[1], word_2[0], word_2[1])
    
    	if word_1 == word_2:
            None
    	else:
    	    if word_2[1] - word_1[1] > 2:
    	    	_check_multigrams(index_1 + 1, min(index_1 + 2, index_last),
                                  count + 1)
    	    else:
    	    	if word_2[1] - word_1[1] == 1:
                    bigram = word_1[0] + ' ' + word_2[0]
                    trigrams_list.append(bigram)
    	    	elif word_2[1] - word_1[1] == 2:
                    trigram = word_1[0] + ' - ' + word_2[0]
                    trigrams_list.append(trigram)
            
    	    	if index_2 == index_last:
                    _check_multigrams(index_1 + 1, index_2, count + 1)
    	    	else:
    	    	    _check_multigrams(index_1, index_2 + 1, count + 1)
    
    _check_multigrams(0, 1)
    
    return trigrams_list

def create_trigrams_file(original_file, new_file, words_to_compare,
                         method="keep", delimiter='\t', word_sep='|', 
                         has_ids=True, trigram_word_sep='|', 
                         encoding='utf-8'):
    """ Takes file of single word texts, strips out
    words you want omitted, then transforms remaining words into
    uni-,bi-,and trigrams, and saves them as a new file
    
    Inputs:
    - original_file = name of file containing original single word texts
    - new_file = name of new file that will contain trigram versions of texts
    - words_to_compare = list of words that you either want to keep or
      remove from texts
    - method = "keep" or "remove" - indicates whether or not words_to_compare
      is for keeping or removing
    - word_sep = how words are separated in original_file
    - trigram_word_sep = how words will be separated in new_file
    """
    MOD_LOGGER.info('Received call to "create_trigrams_file"')

    def _list_to_chunks(li, chunk_size):
    	chunked_list = [
    	    li[i: i + chunk_size]
    	    for i in range(0, len(li), chunk_size)
    	]
    
    	MOD_LOGGER.debug('List of length %s broken into %s chunks',
                         len(li), len(chunked_list))
    
    	return chunked_list

	# use original transcript file (single words) to add trigrams onto;
	# process and write one text at a time to new trigrams file
	MOD_LOGGER.info('Making text generator on single word texts')

	transcript_generator = core.RawCorpus(original_file, 
                                              delimiter, word_sep, 
                                              encoding=encoding,
                                              has_header=False)

	MOD_LOGGER.info('Text generator created on %s', original_file)
	MOD_LOGGER.info('Cleaning texts and making trigrams...')
	MOD_LOGGER.info(
            'Cleaning method = %s words in given word list (%s words)',
            method, len(words_to_compare))

	open(new_file, 'w').close()

	with codecs.open(new_file, 'a+', encoding) as fo:
	    for text_id, text in transcript_generator:
	    	MOD_LOGGER.debug('Current text: %s', {'id': text_id, 'text': text})
            
	    	text_string = word_sep.join(text)
            
	    	words_list = string_to_words_list(text_string, word_sep)
            
	    	MOD_LOGGER.debug('Words list from text string: %s', words_list)
            
	    	clean_words_list = remove_bad_words(words_list, words_to_compare,
                                                    method=method)
            
	    	MOD_LOGGER.debug('Cleaned words list: %s', clean_words_list)
            
	    	if not clean_words_list:
	    	    # if all words in text were bad words, then write an empty line
	    	    string_to_write = str(text_id or '') + '\t' + '\n'
	    	else:
	    	    clean_words_chunks = _list_to_chunks(clean_words_list, 1000)
                    
	    	    trigrams_list = []
	    	    for chunk in clean_words_chunks:
	    	    	trigrams_list.append(make_trigrams(chunk))
	    	    trigrams = sum(trigrams_list, [])
                    
	    	    MOD_LOGGER.debug('Trigrams for current text: %s', trigrams)
                    
	    	    string_to_write = (str(text_id or '') + '\t' +
	    	    	trigram_word_sep.join(trigrams) + '\n')
            
	    	fo.write(string_to_write)

	MOD_LOGGER.info('Saved trigrams to %s', new_file)

