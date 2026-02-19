
from scanner import Scanner


class Parser:
    def __init__(self, filename):
        self.scanner = Scanner(filename)
        self.output = []
        self.variables = []
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
        count = 1 #counter for variable
        while (self.curr_token.type != "NEWLINE"):  #keep reading the array until the \n
            if self.curr_token.type == "VAR":   #if the value is a variable 
                if count == 1: #first variable
                    self.dst = self.curr_token.value
                    if self.curr_token.value not in self.variables:  # avoid duplicates
                        self.variables.append(self.curr_token.value)  #add to the variable list
                    count += 1 #increment for next variable

                elif count == 2:
                    self.operant1 = self.curr_token.value
                    count += 1 

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