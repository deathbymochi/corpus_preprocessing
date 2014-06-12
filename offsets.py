## Functions for getting texts with particular offset ranges

def get_list_subset(mylist, indices=None, min_index=0,
    max_index=None):
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
			
