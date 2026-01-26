class Token:
    def __init__(self, type_, value):
        self.type = type_
        self.value = value

    def __repr__(self):
        return f"Token({self.type}, {repr(self.value)})"

class Scanner:
    def __init__(self, filename):
        ## idk yet

        self.current_char = '' #initialize
        self.next_char() #read next

    def next_char(self):
        #set current char to next char in the file

    def peek(self):
        #still have to do lol

    def get_token(self):
        '''
        reads character then returns token
        '''
        while self.current_char != '':

            # skip spaces, tabs

            # handle \n as a token
            if self.current_char == '\n':
                self.next_char()
                return Token('NEWLINE', '\n')

            # handle integers
            if self.current_char.isdigit():
                number = ''
                while self.current_char.isdigit():
                    number += self.current_char
                    self.next_char()
                return Token('INT', int(num_str))

            # variables
            if self.current_char == 't':                 # t represents the temporary variable
                self.next_char()
                if not self.current_char.isdigit():
                    pass                                  # needs to be some error
                else:
                 var = 't'
                 while self.current_char.isdigit():
                     var += self.current_char
                     self.next_char()

                return Token('VARIABLE', var)
            
            else:                                       # checking for other variables
                if self.current_char.isalpha():
                    var = self.current_char
                    self.next_char()
                    if self.current_char == ' ':
                        return Token("VARAIBLE", var)
                    else:
                        while self.current_char.isalpha():
                            var += self.current_char
                            self.next_char()
                        if var == "live":
                            if self.current_char == ':':
                                self.next_char()            # Eat the colon
                                return Token("LIVE", var)
                        else:
                            pass                    # should return an error but idk how to yet, this means any var with 2+ characters
                        
            # operators
            if self.current_char == '+':
                self.next_char()
                return Token('PLUS', '+')

            if self.current_char == '-':
                self.next_char()
                return Token('MINUS', '-')

            if self.current_char == '*':
                self.next_char()
                return Token('MUL', '*')

            if self.current_char == '/':
                self.next_char()
                return Token('DIV', '/')

            if self.current_char == '=':
                self.next_char()
                return Token('ASSIGN', '=')