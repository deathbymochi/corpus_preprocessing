"""
This module  contains functions for assessing the core language for a body of text,
including:
  - creating a body of core language from texts that omits rare and super-common
    tokens
  - generating a list of tokens that should not be included in the core language
  - saving document frequencies of tokens kept in the body of core language
"""

import gensim as gs
import re
import codecs
import fileinput
import logging

MOD_LOGGER = logging.getLogger('text_processing.corebody')

class RawCorpus(object):
    """Generator object yielding lines from a file containing texts
    (texts are entries per row)

    Inputs:
    - file_name = name of file containing texts
    - delimiter = if there are IDs in the first column, what is the
      column separater (default is tab); if only a single column, put
      'None'
    - word_sep = character that separates each word in the text text
      (default is '|')
    - encoding = what encoding the text file is in; default is utf-8
    """
    def __init__(self, file_name, delimiter='\t', word_sep='|',
                 has_header=True, encoding='utf-8'):
	self.file_name = file_name
	self.encoding = encoding
	self.delimiter = delimiter
	self.word_sep = word_sep
	self.has_header = has_header
	self.num_docs = sum(1 for line in open(self.file_name)) - 1
	self.logger = logging.getLogger('text_processing.corebody.RawCorpus')
	self.logger.info('Found %s texts in %s', self.num_docs, self.file_name)

    def __iter__(self):
        def _line_edit(string):
            string = re.sub(r'(\n|\r)', '', string)
            return string

        with codecs.open(self.file_name, 'r', self.encoding) as fo:
            if self.has_header:
                next(fo)

            for line in fo:
                if self.delimiter is None:
                    text_id = None
                    text_words = _line_edit(line).split(self.word_sep)

                else:
                    if self.delimiter != self.word_sep:
                        try:
                            text_id, text_words = re.split(
                                self.delimiter, _line_edit(line))
                        except ValueError as e:
                            print ("Error in splitting data: make sure "
                                   "you've picked the correct column and "
                                   "word separators")
                            break

                        text_words = text_words.split(self.word_sep)

                    else:
                        row = re.split(self.delimiter, _line_edit(line))
                        text_id = row[0]
                        text_words = row[1:]

                        self.logger.debug('Yields: %s',
                                          {'id': text_id, 'words': text_words})

                yield [text_id, text_words]

def make_simple_core(raw_corp, min_bound=0, max_bound=1.0, tokens_limit=None,
                     encoding='utf-8'):
    """Given a corpus generator object, makes a simple core body of
    single words by using filter methods from gensim Dictionary object

    Inputs:
    - raw_corp = RawCorpus object, which is corpus of all your texts
    - min_bound = minimum number of docs (if int) or percentage of docs
      (if float) that must contain a word for it to be kept in core body;
      default is 0
    - max_bound = maximum number of docs (if int) or percentage of docs
      (if float) that can contain a word for it to be kept in core body;
      default is 1.0, aka 100%
    - tokens_limit = maximum number of tokens resulting core body should
      contain; default is None (no limit)
    - encoding = encoding of text file raw_corp was built on
    """
    MOD_LOGGER.info('Received call to "make_simple_core"')

    # Encode unicode tokens in raw_corp back to byte strings - can't keep tokens in
    # unicode format because gensim Dictionary object expects byte strings
    corp_gen = (
    	[token.encode(encoding)
    	for token in x[1]]
    	for x in raw_corp)

    raw_dict = gs.corpora.Dictionary(corp_gen)

    if type(min_bound) is float:
    	min_bound = min_bound * raw_corp.num_docs

    if type(max_bound) is int:
    	max_bound = float(max_bound) / raw_corp.num_docs

    MOD_LOGGER.debug('Thresholds used: %s',
    	{'min': min_bound, 'max': max_bound})

    raw_dict.filter_extremes(min_bound, max_bound, tokens_limit)
    raw_dict.compactify()

    return raw_dict

def get_bad_ids_from_gs_dict(gs_dict, min_bound, max_bound):
    """Gets a list of bad ids (token ids that are below a min threshold,
    and above a max threshold)
    """
    bad_ids = [
        id
        for id in gs_dict.dfs
        if (
        	gs_dict.dfs[id] < min_bound
        	or gs_dict.dfs[id] > max_bound
        )
    ]

    return bad_ids

def get_wordlist_using_token_ids(gs_dict, token_ids):
    """Returns a list of tokens from a gensim dict whose ids match
    the given list
    """
    return [token for (id, token) in gs_dict.items()
    for id in token_ids]

def delete_first_col_from_file(file_name):
    """Deletes leftmost column from a file that already contains data
    in it
    """
    for line in fileinput.input(file_name, inplace=True):
    	remainder = line.split()[1:]
    	print ' '.join(remainder)

def add_header_to_file(file_name, header_space_sep):
    """Adds a header to a file that already contains data in it

    Inputs:
    - file_name = file you want to add a header to
    - header_space_sep = string that contains your header, separated by
      spaces (EX: 'col1 col2 col3')
    """
    header = header_space_sep.split()
    for line in fileinput.input(file_name, inplace=True):
    	if fileinput.isfirstline():
    		print ' '.join(header)
    	print line,

def write_dfs_to_file(corebody, file_name, ids_keep=None, ids_remove=None,
                      header='token doc_freq'):
    """Saves tokens and their document frequencies to a txt file;
    file has a header
    """
    corebody.filter_tokens(ids_remove, ids_keep)
    corebody.save_as_text(file_name)
    delete_first_col_from_file(file_name)
    add_header_to_file(file_name, header)

def create_corebody(text_file, new_filename=None, delimiter='\t',
                    word_sep='|', min_docnum=0, max_docnum=1.0,
                    tokens_limit=None, encoding='utf-8'):
    """Creates core body of language for text sample (all words
    in sample meeting a minimum document threshold, and their document
    frequencies) as gensim dict object. Also creates two txt files, a
    corebody file containing words kept in corebody, and a badwords file
    containing words that were excluded (naming = text_file +
    {'badwords'|'corebody'})

    Inputs:
    - text_file = file containing texts
    - delimiter = char separating cols ('None' if only one col in data)
    - word_sep = char separating words in text text
    - min_docnum = min num docs for words to be included in core body
    - max_docnum = max num docs for words to be included in core body
    - tokens_limit = max number of words to include in core body
    - encoding = encoding of text file
    """
    MOD_LOGGER.info('Received call to "create_corebody"')
    MOD_LOGGER.info('Making text generator object...')
    text_generator = RawCorpus(
    	text_file, delimiter, word_sep, encoding=encoding)

    MOD_LOGGER.info('Text generator created on %s', text_file)

    MOD_LOGGER.info('Creating core body of all tokens...')
    text_corebody = make_simple_core(text_generator)

    # write file containing all token dfs
    if new_filename is None:
    	alldfs_file = text_file[:-4] + '_dfs-all.txt'
    else:
    	alldfs_file = new_filename

    write_dfs_to_file(text_corebody, alldfs_file)

    MOD_LOGGER.info('Wrote dfs of all tokens to %s', alldfs_file)

    # filter out bad words
    ## filter_extremes() method of gensim Dictionary object requires max
    ## threshold to be given as percent of all docs
    if max_docnum == 0 or max_docnum == 1.0:
    	max_bound = 1.0
    else:
    	max_bound = float(max_docnum) / text_generator.num_docs

    MOD_LOGGER.info('Filtering core body using: %s',
    	{'min docs': min_docnum, 'max perc': max_bound})
    text_corebody.filter_extremes(min_docnum, max_bound, tokens_limit)

    return text_corebody
