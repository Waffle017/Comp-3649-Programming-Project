from instruction import readIn


class Token:
    def __init__(self, type_, value):
        self.type = type_
        self.value = value

    def __repr__(self):
        return f"Token({self.type}, {repr(self.value)})"

class Scanner:
    def __init__(self, filename):
        intaken = readIn(filename)
        if intaken is None or len(intaken) == 0:
            self.content = ''
            self.current_char = ''
        else:
            self.content = ''.join(intaken)
            self.current_char = self.content[:1]

        self.index = 1


    def next_char(self):
        if self.index < len(self.content):
            self.current_char = self.content[self.index]
            self.index += 1
        else:
            self.current_char = ''
        

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
                return Token('INT', int(number))
            
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
            
            if self.current_char == '':
                self.next_char()
                return Token('Colon', ':')
            # skip spaces and tabs
            if self.current_char in [' ', '\t']:
                self.next_char()
                continue

            # handle variables (letters)
            if self.current_char.isalpha(): #check if its a letter                
                var_name = '' #initalize variable name
                while self.current_char.isalnum() or self.current_char == '_': #this allows t1 etc to be variable nanmes and not just t
                    var_name += self.current_char # adds to variable name  1 char at a time
                    self.next_char()
                    if self.current_char == '': #if its a space or tab -> break
                        break
                
                if var_name == 'live':
                    return Token('END', 'live') #temporarily calling it this for now
                return Token('VAR', var_name) 

            # unknown (not any of the above)
            char = self.current_char
            self.next_char()
            return Token('UNKNOWN', char)

        return None  

#test code: this is temporarily here to test scanner
if __name__ == "__main__":
    scanner = Scanner("programpara.txt")
    tokens = []
    while True:
        token = scanner.get_token()
        if token is None:
            break
        tokens.append(token)
        print(token)
    
class Parser:
    def __init__(self, filename):
        self.scanner = Scanner(filename)
        self.output = []
        self.curr_token = self.scanner.get_token()


    def match(self, expected_type):
        if self.curr_token.type == expected_type:
            self.curr_token = self.scanner.get_token()

        else:
            raise ValueError("Error")
        
    def readIntermediateCode(self):
        while self.curr_token.type != "LIVE":
            instruction = self.read3AddrInstruction()
            self.output.append(instruction)

        return self.output



    def read3AddrInstruction(self):

            



            
   


