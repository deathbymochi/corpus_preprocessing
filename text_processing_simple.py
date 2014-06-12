# Script to return most frequently occurring one-, two-, and
# three-word phrases in a sample  of texts (as a file w/ rows 
# of texts) using user input for file names and other arguments
#------------------------------------------------------------------
import corebody as core
import trigrams as trigrams
from distutils import util
import script_utils as script
import logging

format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

logging.basicConfig(level=logging.INFO, format=format,
    datefmt='%m-%d %H:%M', filename='simple.log')

LOGGER = logging.getLogger('text_processing')
LOGGER.setLevel(logging.INFO)

def get_filename():
    """Get filename from user input
    """
    prompt = 'Name of file containing texts (.csv or .txt):'
    try_func = lambda x: open(x).close()
    error = IOError
    error_message = ("Unable to open file - "
        "please check spelling and enter again")

    # Test that file given can be opened
    target_file = script.get_user_input(prompt, try_func, error,
        error_message)

    return target_file

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
    """Get thresholds used to define corebody (min and max doc num)
    """
    prompts = {
        'min': 'Min num of texts that a word must appear in\n \
                (if no min, enter 0):',
        'max': 'Max num of texts that a word can appear in\n \
                (if no max, enter 0):'
    }
    try_func = lambda x: int(x)
    error = ValueError
    error_message = "Error: please enter a valid digit"

    # Test that min_docnum given is a valid integer
    min_docnum = script.get_user_input(prompts['min'], try_func, error,
        error_message, True)

    # Test that max_docnum given is a valid integer
    max_docnum = script.get_user_input(prompts['max'], try_func, error,
        error_message, True)

    return min_docnum, max_docnum

def user_input_corebody_params():
    """Prompt user to input file name and other arguments needed to pass
    to core.create_corebody()
    """
    args = []
    kwargs = {}

    target_file = get_filename()
    has_ids, kwargs['delimiter'], kwargs['word_sep'] = get_file_parameters()
    kwargs['min_docnum'], kwargs['max_docnum'] = get_corebody_thresholds()

    args.append(target_file)

    return (args, kwargs, has_ids)

def main():
    """Prompts for user inputs and runs text processing procedure on user
    inputs
    """
    NUM_TRIGRAM_TOKENS = 200 #POTENTIALLY GET USR INPUT ABOVE (currently 200)

    LOGGER.info('Starting.......................................')

    # create core body of single words, save single word dfs to file
    corebody_params = user_input_corebody_params()
    corebody_params[1]['encoding'] = 'latin1'

    target_file = corebody_params[0][0]
    delimiter = corebody_params[1]['delimiter']
    word_sep = corebody_params[1]['word_sep']
    min_docnum = corebody_params[1]['min_docnum']
    max_docnum = corebody_params[1]['max_docnum']
    encoding = corebody_params[1]['encoding']
    has_ids = corebody_params[2]

    corebody = core.create_corebody(*corebody_params[0], **corebody_params[1])
    core_words = [word for (id, word) in corebody.items()]

    # using core body of single words to edit out too rare or too common
    # words, break texts down into trigrams, save trigram'd texts to file
    trigrams_file = target_file[:-4] + '_trigrams.txt'
    trigrams.create_trigrams_file(target_file, trigrams_file, core_words,
        has_ids=has_ids, delimiter=delimiter, word_sep=word_sep,
        encoding=encoding)

    # create core body of trigrams, save trigram dfs to file
    corebody_trigrams = core.create_corebody(trigrams_file,
        tokens_limit=NUM_TRIGRAM_TOKENS, encoding=encoding)

    top_trigrams_file = 'top' str(NUM_TRIGRAM_TOKENS) + '_trigrams.txt')

    LOGGER.info('Writing top %s trigrams to %s', NUM_TRIGRAM_TOKENS,
        top_trigrams_file)
    core.write_dfs_to_file(corebody_trigrams, top_trigrams_file)

    LOGGER.info('Finished.......................................')

if __name__ == '__main__':
    main()
