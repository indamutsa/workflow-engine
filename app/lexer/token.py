# This class extracts tokens and provide us with a list that can be parsed

######################
# Token class
######################

# A token class should have a type and the value. The text read are extracted and we assign a value and type of the created tokem
# before we insert in the list
class Token:
    def __init__(self, type_, value=None, pos_start=None, pos_end=None):
        self.type = type_
        self.value = value

        if pos_start:
            self.pos_start = pos_start.copy()
            self.pos_end = pos_start.copy()
            self.pos_end.increment_position()

        if pos_end:
            self.pos_end = pos_end
    # Determines if we are going to perform either a keyword and identifier part of
    # the function or if we perform the term inside the expression function
    def matches(self, type_, value):
        return self.type == type_ and self.value == value

    def __repr__(self):
        return f'{self.type} : {self.value}' if self.value else f'{self.type}'

 
