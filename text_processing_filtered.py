# Script to generate 'most important' one-, two-, and three-word
# phrases for a sample of texts (as a single file with rows of texts),
# using a second sample of texts as a filter
#
# Script prompts for user input for file names and other arguments
#------------------------------------------------------------------

import corpus_preprocessing.core.corebody as core
import corpus_preprocessing.core.trigrams as edit
import corpus_preprocessing.core.compare_corpus as compare
from distutils import util
import logging
import corpus_preprocessing.script_utils as script

format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

logging.basicConfig(level=logging.INFO, format=format,
    datefmt='%m-%d %H:%M', filename='filtered.log')

LOGGER = logging.getLogger('text_processing')
LOGGER.setLevel(logging.INFO)

def get_filenames():
    """Get filenames of file containing target texts and file containing
    filter texts from user input
    """
    prompts = {
        'target': 'Name of file containing target texts (.csv or .txt):',
        'filter': 'Name of file containing texts to filter on (.csv or .txt):'
    }
    try_func = lambda x: open(x).close()
    error = IOError
    error_message = ("Unable to open file - "
        "please check spelling and enter again")

    # Test that target file given can be opened
    target_file = script.get_user_input(prompts['target'], try_func, error,
        error_message)

    # Teset that filter file given can be opened
    filter_file = script.get_user_input(prompts['filter'], try_func, error,
        error_message)

    return target_file, filter_file

def get_file_parameters():
    """Get file parameters (column delimiter, word separater) from user input
    """
    prompt = 'IDs are included in file? (y/n):'
    try_func = lambda x: bool(util.strtobool(x))
    error = ValueError
    error_message = "Error: please enter y or n"

    # Test that valid yes or no response is given for has_ids
    has_ids = script.get_user_input(prompt, try_func, error, error_message,
        True)

    if has_ids:
        delimiter = raw_input(
            'Character your file columns are separated by\n \
            (EX: / | , :) (if space or tab, enter a space or tab): \n')
    else:
        delimiter = None

    word_sep = raw_input(
        'Character your text words are separated by\n \
        (EX: / | , .) (if space, enter a space): \n')

    return has_ids, delimiter, word_sep

def get_corebody_thresholds():
    """Get thresholds used to define corebody (min doc num)
    """
    prompt = 'Min num of texts that a word must appear in\n \
                (if no min, enter 0):'
    try_func = lambda x: int(x)
    error = ValueError
    error_message = "Error: please enter a valid digit"

    # Test that min_docnum given is a valid integer
    min_docnum = script.get_user_input(prompt, try_func, error,
        error_message, True)

    return min_docnum

def user_input_corebody_params():
    """Prompt user to input file name and other arguments needed to pass
    to core, edit, and compare module functions
    """
    args = []
    kwargs = {}

    target_file, filter_file = get_filenames()
    has_ids, kwargs['delimiter'], kwargs['word_sep'] = get_file_parameters()
    min_docnum = get_corebody_thresholds()

    args.append(target_file)

    return (args, kwargs, filter_file, has_ids, min_docnum)

def main():
    """Prompts for user inputs and runs text processing procedure on user
    inputs
    """
    PVAL_THRESHOLD = 0.25 #POTENTIALLY ASK FOR USR INPUT ABOVE (currently 0.25)
    MIN_MULTIPLIER = 2 #POTENTIALLY ASK FOR USR INPUT ABOVE (currently 2)

    LOGGER.info('Starting.......................................')

    # create core body of single words from target texts,
    # save single word dfs to file
    corebody_params = user_input_corebody_params()
    corebody_params[1]['encoding'] = 'cp1252'

    target_file = corebody_params[0][0]
    delimiter = corebody_params[1]['delimiter']
    word_sep = corebody_params[1]['word_sep']
    encoding = corebody_params[1]['encoding']
    filter_file = corebody_params[2]
    has_ids = corebody_params[3]
    min_docnum = corebody_params[4]

    LOGGER.info('Creating corebody of single words from target texts...')
    corebody = core.create_corebody(*corebody_params[0],
        **corebody_params[1])

    # do same for filter texts - create core body of single words,
    # save to file
    LOGGER.info('Creating corebody of single words from filter texts...')
    filterbody = core.create_corebody(filter_file,
        **corebody_params[1])

    # merge corebody and filterbody, conduct t-tests on token dfs between
    # two, save tokens and pvals of t-tests to file
    LOGGER.info('Merging corebody and filterbody for df comparison...')
    mergedbody = compare.merge_two_cores(corebody, filterbody)

    # Look for back and fwd slash in case there's a directory in the file path
    directory_index = max(target_file.rfind('/'),
        target_file.rfind('\\')) + 1

    ttest_file = (target_file[:-4] + '_' +
        filter_file[directory_index:-4] +
        '_' + 'df-ttest.txt')
    compare.write_df_ttest_to_file(mergedbody, corebody.num_docs,
        filterbody.num_docs, ttest_file, min_docnum)

    # use list of 'significant' (below pval threshhold) single words
    # from df ttest between corebody and filterbody to edit out 'meaningless'
    # single words from texts, break filtered texts down into trigrams,
    # save corebody and filterbody trigram'd texts to file
    LOGGER.info(
        'Creating generator obj returning words from %s with pval < %s',
        ttest_file, PVAL_THRESHOLD)
    sig_words_generator = compare.words_below_pval_generator(ttest_file,
        PVAL_THRESHOLD, encoding=encoding)
    sig_words = list(sig_words_generator)

    LOGGER.info('List of %s sig words created', len(sig_words))

    corebody_trigrams_file = target_file[:-4] + '_trigrams.txt'
    filterbody_trigrams_file = filter_file[:-4] + '_trigrams.txt'

    LOGGER.info("Creating trigram'd target texts at %s",
        corebody_trigrams_file)
    edit.create_trigrams_file(target_file, corebody_trigrams_file,
        sig_words, has_ids=has_ids, delimiter=delimiter,
        word_sep=word_sep, encoding=encoding)

    LOGGER.info("Creating trigram'd filter texts at %s",
        filterbody_trigrams_file)
    edit.create_trigrams_file(filter_file, filterbody_trigrams_file,
        sig_words, has_ids=has_ids, delimiter=delimiter,
        word_sep=word_sep, encoding=encoding)

    # create cores for corebody and filterbody trigrams, then merge together
    # for df comparison
    LOGGER.info('Creating corebody of trigrams from target texts...')
    corebody_trigrams = core.create_corebody(corebody_trigrams_file,
        encoding=encoding)

    LOGGER.info('Creating corebody of trigrams from filter texts...')
    filterbody_trigrams = core.create_corebody(filterbody_trigrams_file,
        encoding=encoding)

    LOGGER.info(
        "Merging trigram'd corebody and filterbody for df comparison...")
    mergedbody_trigrams = compare.merge_two_cores(corebody_trigrams,
        filterbody_trigrams)

    # conduct ttests on token dfs between corebody and filterbody trigrams
    # ignoring tokens with total df below min_docnum and multiplier
    # below min_multiplier in order to arrive at a saved list of
    # 'significant trigrams'
    ttest_file_trigrams = 'top_trigrams.txt'

    LOGGER.info(
        "Finding 'significant tokens' for target texts using mult of %s",
        MIN_MULTIPLIER)
    compare.write_df_ttest_to_file(mergedbody_trigrams,
        corebody_trigrams.num_docs, filterbody_trigrams.num_docs,
        ttest_file_trigrams, min_docnum, MIN_MULTIPLIER, PVAL_THRESHOLD)

    LOGGER.info("Sorting sig tokens file by pval (asc), scope (desc)")
    script.sort_file(ttest_file_trigrams, [1, 2], [False, True], col_sep=',',
        transform=lambda x: float(x))

    LOGGER.info('Finished.......................................')

if __name__ == '__main__':
    main()




