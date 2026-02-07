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
                    return Token('LIVE', 'live') #temporarily calling it this for now
                return Token('VAR', var_name) 

            # unknown (not any of the above)
            char = self.current_char
            self.next_char()
            return Token('UNKNOWN', char)

        return None  
    
class Parser:
    def __init__(self, filename):
        self.scanner = Scanner(filename)
        self.output = []
        self.curr_token = self.scanner.get_token()

    #match the token then delete
    def match(self, expected_type): 
        if self.curr_token.type == expected_type:
            self.curr_token = self.scanner.get_token()

        else:
            raise ValueError("Error")
        
    #Keep reading the tokens until LIVE
    def readIntermediateCode(self):
        while self.curr_token.type != "LIVE":
            instruction = self.read3AddrInstruction() #get the single instruction
            self.output.append(instruction) #add it to the output array 
        
        if self.curr_token.type == "LIVE":
            self.match("LIVE")
        
        return self.output

    #read the single instruction
    def read3AddrInstruction(self):
        count = 0 #counter for variable
        while (self.curr_token.value != "\n"):  #keep reading the array until the \n
            if self.curr_token.type == "VAR":   #if the value is a variable 
                count += 1
                if count == 1:
                    self.dst = self.curr_token.value
                elif count == 2:
                    self.operant1 = self.curr_token.value
                else:
                    self.operant2 = self.curr_token.value
                self.match("VAR")
            
            if self.curr_token.type == "ASSIGN": #consume the equal
                self.match("ASSIGN")


            if self.curr_token.type == "INT":   #handle integer
                count += 1
                if count == 2:
                    self.operant1 = self.curr_token.value
                else:
                    self.operant2 = self.curr_token.value

                self.match("INT")
    
            if self.curr_token.type == "MINUS": #handle either NEG or SUB
                self.operator = self.curr_token.value
                self.match("MINUS")

         
            if self.curr_token.type in ["PLUS", "MUL", "DIV"]: #handle rest of operators 
                self.operator = self.curr_token.value
                self.match(self.curr_token.type)

        self.match("NEWLINE") #get rid of the \n in array
        return [self.dst, self.operant1, self.operator, self.operant2]




#test code: this is temporarily here to test scanner, uh claude did this part whoops 
if __name__ == "__main__":
    print("=== SCANNER TEST ===")
    scanner = Scanner("programpara.txt")
    tokens = []
    while True:
        token = scanner.get_token()
        if token is None:
            break
        tokens.append(token)
        print(token)
    
    print("\n=== PARSER TEST ===")
    try:
        parser = Parser("programpara.txt")
        print(f"Parser initialized. Current token: {parser.curr_token}")
        
        # Add debug to readIntermediateCode
        while parser.curr_token.type != "LIVE":
            print(f"\nProcessing instruction, current token: {parser.curr_token}")
            instruction = parser.read3AddrInstruction()
            print(f"Got instruction: {instruction}")
            parser.output.append(instruction)
        
        print("\nParsed Instructions:")
        for i, instruction in enumerate(parser.output):
            print(f"Instruction {i+1}: {instruction}")
            if len(instruction) == 4:
                dst, op1, operator, op2 = instruction
                print(f"  {dst} = {op1} {operator} {op2}")
    except Exception as e:
        print(f"Error occurred: {e}")
        import traceback
        traceback.print_exc()


         





            
   


