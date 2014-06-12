## Functions useful for running the user input scripts

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
