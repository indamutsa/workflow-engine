def error_pointer(text, pos_start, pos_end):

    result = ''

    # Calculate indices
    # We take the last occurrence index of the new line
    index_start = max(text.rfind('\n', 0, pos_start.index), 0)
    index_end = text.find('\n', index_start + 1)

    if index_end < 0:
        index_end = len(text)

    # Generate each line
    line_count = pos_end.line_num - pos_start.line_num + 1
    for i in range(line_count):

        # Calculate line columns
        line = text[index_start:index_end]
        # A problem to fix at the end
        col_start = pos_start.column_num if i == 0 else 0
        col_end = pos_end.column_num if i == line_count - 1 else len(line) - 1

        # Append to result
        result += line + '\n'
        result += ' ' * col_start + '^' * (col_end - col_start)

        # Re-calculate indices
        index_start = index_end
        index_end = text.find('\n', index_start + 1)
        if index_end < 0:
            index_end = len(text)

    return result.replace('\t', '')
