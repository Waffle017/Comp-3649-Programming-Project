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
