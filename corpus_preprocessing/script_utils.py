"""
This module contains utility functions, functions  useful 
for running the user input scripts and for culling subsets of a body
of texts (EX: get a corpus of only the last X words in the texts)
"""

def get_user_input(raw_input_string, func_to_try, exception,
    exception_message, return_func_val=False):
    '''Creates 'while True, try... except' loop for given
    user input taken from raw_input(), trying the given function and
    excepting the given error

    Inputs:
    - raw_input_string = the message to print when prompting user
      for input from the command line
    - func_to_try = the function to pass the user input to, to check
      that conditions are met
    - exception = the error to except (EX: IOError)
    - exception_message = the message to print when exception is raised
    - return_func_val = whether or not you want to return the result of
      func_to_try rather than just the raw user_input
    '''
    while True:
        try:
            user_input = raw_input(raw_input_string + '\n')
            if return_func_val:
                user_input = func_to_try(user_input)
            else:
                func_to_try(user_input)
            break
        except exception as e:
            print exception_message

    return user_input

def sort_file(filename, keycol_list, reverse_list, col_sep='\t',
    has_header=False, transform=lambda x: x):
    """Sorts file in order based on given column indices
    (first column = 0, second = 1, etc.) and whether or not each
    key should be in ascending/descending order

    Inputs:
    - keycol_list = list of col indices
    - reverse_list = list of True if descending and Fales if ascending, for
      each col in keycol_list
    - col_sep = char that delimits file columns
    - has_header = if True, skip first line
    - transform = function to transform data type of col if need to
      (like str -> int)
    """
    with open (filename, 'r+') as fo:
        if has_header:
            fo.next()

        data = []
        for line in fo:
            data.append(line.split(col_sep))

        ordering = zip(keycol_list, reverse_list)

        # reverse b/c need to start with secondary sorts first
        ordering.reverse()

        for sorting in ordering:
           data.sort(key=lambda line: (transform(line[sorting[0]])),
            reverse=sorting[1])

        fo.seek(0)
        for line in data:
            fo.write(col_sep.join(line))

def get_list_subset(mylist, indices=None, min_index=0,
                    max_index=None):
    """Returns a subset of a list according to given indices, that 
    correspond to each list element, or if no indices are given, the 
    indices of the python list object. The indices should be ordinal,
    but don't have to have the same intervals
    
    Inputs:
    - mylist = list (EX: ['a', 'b', 'c'])
    - indices = given indices for each element of mylist (EX: [0, 3, 8])
    - min_index = min cutoff point for getting the subset
    - max_index = max cutoff point for getting the subset
    """
    if indices is None:
        indices = range(len(mylist))

    indexed_list = zip(mylist, indices)

    if max_index is None:
        max_index = indices[-1] + 1

    if min_index < 0:
        min_index = max(0, max_index + min_index)

    subset = (
        elem
        for (elem, i) in indexed_list
        if (
            min_index <= i < max_index
        )
    )

    return subset

def create_subset_texts(text_file, new_file, col_sep='\t', word_sep='|', 
                        min_index=0, max_index=None, has_ids=True):
    """ Creates new text file that contains the desired subsets of the
    original texts (EX: only the first 200 words of each text)
    
    Inputs:
    - text_file = file containing original texts, indices to be used for
      subsetting should be in col to the right of col containing texts
    - new_file = name of new file containing only subsets
    - col_sep = column separator in text_file, will also be used in new_file
    - word_sep = word delimiter in text_file, will also be used in new_file
    - min_index = min cutoff point for getting the subset
    - max_index = max cutoff point for getting the subset
    - has_ids = if True, IDs are in first col of text_file, otherwise
      texts are in first col
    """
    with open(text_file, 'r') as f1, open (new_file, 'w') as f2:
        if has_ids:
            text_col, offset_col = 1, 2
        else:
            text_col, offset_col = 0, 1
            textid = 0

        for row in f1:
            line = row.split(col_sep)
            word_list = line[text_col].split(word_sep)
            offset_list = line[offset_col].split(word_sep)
            offset_list = [float(x) for x in offset_list]

            subset = get_list_subset(word_list, offset_list, min_index,
                max_index)

            if has_ids:
                textid = line[0]
            else:
                textid += 1

            new_line = str(textid) + '\t' + '|'.join(subset) + '\n'
            f2.write(new_line)
			
