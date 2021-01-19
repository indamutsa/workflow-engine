####################
# Lexical analyzer
####################

from app.lexer.token import Token
from app.utils.position import Position

from app.constants.constant import *
from app.errors.error import *
from app.errors.error import *

from app.utils.position import Position



class Lexer:
    def __init__(self, filename, file_text):
        self.filename = filename
        self.file_text = file_text
        self.pos = Position(-1, 0, -1, filename, file_text) # -1 because it does not exist when we start, we can assign it anything
        self.current_char = None
        self.increment_char() # This will help our index start from zero when the class is used

    # This function will step up through the script (text) submitted while keeping the current index
    def increment_char(self): 
        self.pos.increment_position(self.current_char) 
        self.current_char = self.file_text[self.pos.index] if self.pos.index < len (self.file_text) else None # assign it only when we haven't reached the end of the file

    def generate_tokens(self):
        token_list = []
        # pdb.set_trace()
        # Here we are simply checking the current character and then appending to the token
        while self.current_char != None:
            if self.current_char in ' \t':
                self.increment_char()

            elif self.current_char == '#':
                self.skip_comment()

            elif self.current_char in ';\n':
                _token = Token(TokenType['newline'], pos_start = self.pos)     
                token_list.append(_token)
                self.increment_char()

            elif self.current_char in digits:
                _token = self.generate_number()
                token_list.append(_token)

            elif self.current_char in letters:
                _token = self.generate_identifier()
                token_list.append(_token)

            elif self.current_char == '"':
                _token = self.generate_string()
                token_list.append(_token)

            elif self.current_char == '+':
                _token = Token(TokenType['_plus'], pos_start = self.pos)     
                token_list.append(_token)
                self.increment_char()

            elif self.current_char == '-':
                _token = self.generateMinusOrArrow()     
                token_list.append(_token)

            elif self.current_char == '*':
                _token = Token(TokenType['_mult'], pos_start = self.pos)
                token_list.append(_token)
                self.increment_char()

            elif self.current_char == '/':
                _token = Token(TokenType['_div'], pos_start = self.pos)
                token_list.append(_token)
                self.increment_char()

            elif self.current_char ==  '(':
                _token = Token(TokenType['_lparen'], pos_start = self.pos)
                token_list.append(_token)
                self.increment_char()
            

            elif self.current_char == ')':
                _token = Token(TokenType['_rparen'], pos_start = self.pos)
                token_list.append(_token)
                self.increment_char()

            elif self.current_char ==  '[':
                _token = Token(TokenType['_lsquare'], pos_start = self.pos)
                token_list.append(_token)
                self.increment_char()
            

            elif self.current_char == ']':
                _token = Token(TokenType['_rsquare'], pos_start = self.pos)
                token_list.append(_token)
                self.increment_char()

            elif self.current_char ==  '^':
                _token = Token(TokenType['_pow'], pos_start = self.pos)
                token_list.append(_token)
                self.increment_char()
            
            elif self.current_char == ',':
                _token = Token(TokenType['_comma'], pos_start=self.pos)
                token_list.append(_token)
                self.increment_char()

            # This for not operator
            elif self.current_char == '!':
                token, error = self.generate_not_equals()
                if error: return [], error
                token_list.append(token)

            # This is for equals operator
            elif self.current_char == '=':
                token_list.append(self.generate_equals())

            elif self.current_char == '<':
                token_list.append(self.generate_less_than())

            elif self.current_char == '>':
                token_list.append(self.generate_greater_than())

            

            else:
                # We are going to return an error
                illegal_char =  self.current_char
                pos_start = self.pos.copy() 
                self.increment_char()
                return [], IllegalCharacter(pos_start, self.pos , "** "+ illegal_char + " **")

        # We add the token for the end of text to make sure we know when the file ends
        file_end_token = Token(TokenType['_eof'], pos_start= self.pos)
        token_list.append(file_end_token)
        # print(token_list)
        return token_list, None
        

    # This function differentiate integer and float
    def generate_number(self):
        pos_start = self.pos.copy()
        pos_start1 = pos_start
        pos_start = None
        num_of_dot = 0
        digit_str = ''
        
        # We are checking if the current char is a digit or a dot
        while self.current_char != None and self.current_char in digits + '.':
            if '.' == self.current_char:
                if num_of_dot == 1: break 
                num_of_dot = num_of_dot + 1
                digit_str += '.'

            else:
                # There can only be one . in a number in a case of the float
                digit_str += self.current_char
            self.increment_char()
    
        # The returned char is of type int, and we return its value as well
        if num_of_dot == 0:
            return Token(TokenType['_int'], int(digit_str), pos_start1, self.pos)
        else: # The current character is of type float, and we return the value wrapped in Token object
            return Token(TokenType['_float'], float(digit_str), pos_start1, self.pos)

    # This method generate a keyword such as var or identifier such as variable
    def generate_identifier(self):
        keyword_str = ''
        pos_start = self.pos.copy()
        keywords_list = list(TokenType['keywords'].values())

        keyword = TokenType['keyword']
        identifier = TokenType['identifier']


        # We check if the current char is among the digits, letters or underscore. 
        # Both the keyword and identifier such as varible can be among the above text( letters_digits)
        while self.current_char != None and self.current_char in letters_digits + '_':
            keyword_str += self.current_char
            self.increment_char()

        # We retrieve the token type, it can be a keyword(such as var) or an identifier(such as variable name)
        token_type = keyword if keyword_str in keywords_list else identifier
        return Token(token_type, keyword_str, pos_start, self.pos)

    # This method generate not equals token !
    def generate_not_equals(self):
        pos_start = self.pos.copy()
        self.increment_char()
        _ne = TokenType['_ne']

        if self.current_char == '=':
            self.increment_char()
            return Token(_ne, pos_start=pos_start, pos_end=self.pos), None

        self.increment_char()
        return None, ExpectedCharError(pos_start, self.pos, "'=' (after '!')")

    def generate_equals(self):
        token_type = TokenType['_eq']
        pos_start = self.pos.copy()
        self.increment_char()

        if self.current_char == '=':
            self.increment_char()
            token_type = TokenType['_ee']

        return Token(token_type, pos_start=pos_start, pos_end=self.pos)

    def generate_less_than(self):
        token_type = TokenType['_lt']
        pos_start = self.pos.copy()
        self.increment_char()

        if self.current_char == '=':
            self.increment_char()
            token_type = TokenType['_lte']

        return Token(token_type, pos_start=pos_start, pos_end=self.pos)

    def generate_greater_than(self):
        token_type = TokenType['_gt']
        pos_start = self.pos.copy()
        self.increment_char()

        if self.current_char == '=':
            self.increment_char()
            token_type = TokenType['_gte']

        return Token(token_type, pos_start=pos_start, pos_end=self.pos)


    def generateMinusOrArrow(self):
        token_type = TokenType['_minus']
        pos_start = self.pos.copy()
        self.increment_char()

        if self.current_char == '>':
            self.increment_char()
            token_type = TokenType['_arrow']

        return Token(token_type, pos_start=pos_start, pos_end=self.pos)


    def generate_string(self):
        string = ''
        pos_start = self.pos.copy()
        escape_character = False
        self.increment_char()

        escape_characters = {
            'n': '\n',
            't': '\t'
        }

        # We append the string accordingly by taking taking in consideration the exceptions such as tab, newline and backslashes
        while self.current_char != None and (self.current_char != '"' or escape_character):
            if escape_character:
                string += escape_characters.get(self.current_char, self.current_char)
            else:
                # When we meet a backslash, we are escaping python backslash, that's why it is double
                if self.current_char == '\\':
                    escape_character = True
                else:
                    string += self.current_char
            self.increment_char()
            escape_character = False
        
        self.increment_char()
        return Token(TokenType['_string'], string, pos_start, self.pos)


    def skip_comment(self):
        self.increment_char()

        while self.current_char != '\n':
            self.increment_char()

        self.increment_char()    
