class Instruction:
    def __init__(self, dest, src1, op, src2=None):
        # we initialize here guys like line.string = read input

        self.dest = dest
        self.src1 = src1
        self.src2 = src2
        self.op = op

    def __str__(self):
        # Unary negation, example: dest = -src
        if self.op == "NEG":
            return f"{self.dest} = -{self.src1}"

        # Simple assignment, dest = src
        elif self.op == "=":
            return f"{self.dest} = {self.src1}"
        
        # Binary operation, dest = src1 op src2
        else:
            return f"{self.dest} = {self.src1} {self.op} {self.src2}"
        

class Asm_Instruction:
    def __init__(asm, opcode, dst, src):
        asm.opcode = opcode
        asm.dst = dst
        asm.src = src


def readIn(filename):
    file_path = f"/Users/scottlouden/Downloads/Github/Paradigm/{filename}"
    lines = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            for line in file:
                if (line.strip() != ""):  # make sure we dont add empty lines
                    tokens = line.split()  # Split by spaces
                    for token in tokens: #loop through stripped tokens
                        lines.append(token)  # Append tokens to list
                    lines.append("\n")  # Add empty string between each line to mark new line
    except FileNotFoundError:
        print(f"File not found")
        return None #idk if its NULL or Null or None doesn't matter much

    return lines



lines = readIn("programpara.txt") # reads in the file, can be changed depending on txt file name
print(lines) #error checking 


