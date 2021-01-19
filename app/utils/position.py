# This section keeps the position of the text provided

class Position:
    def __init__(self, index, line_num, column_num, filename, file_text):
        self.index = index
        self.line_num = line_num
        self.column_num = column_num
        self.filename = filename
        self.file_text = file_text

    # We default current_char = None to make the current_char unrequired
    def increment_position(self, current_char=None):
        self.index += 1
        self.column_num += 1

        if current_char == '\n':
            self.line_num += 1
            self.column_num = 0

        return self

    def copy(self):
        return Position(self.index, self.line_num, self.column_num, self.filename, self.file_text)


    