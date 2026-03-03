import os
import sys
from parser import Parser
from allocator import build_interference_graph
from instruction import Asm_Instruction 

# Step 6: Code Generation function (Stub to fill in later)
def generate_assembly(intermediate_instructions, register_mapping):
    asm_output = []

    def format_operand(op):
        reg_num = register_mapping.get(op)
        if reg_num is not None:
            return f"R{reg_num}"
        return str(op)
    
    # dictionary for mapping symbols to assembly OPCODES
    opcode_map = {
        '+': 'ADD',
        '-': 'SUB',
        '*': 'MUL',
        '/': 'DIV'
    }

    # Loop through instructions
    for instr in intermediate_instructions:
        dest_reg = format_operand(instr.dest)
        src1_formatted = format_operand(instr.src1)

        # Move source 1 into destination register
        if dest_reg != src1_formatted:
            asm_output.append(Asm_Instruction("MOV", dest_reg, src1_formatted))

        # If this is a binary operation, do the math
        if instr.op in opcode_map and instr.src2 is not None:
            src2_formatted = format_operand(instr.src2)
            opcode = opcode_map[instr.op]
            asm_output.append(Asm_Instruction(opcode, dest_reg, src2_formatted))

    return asm_output

def main():
    # Step 1: Check for command-line arguments
    if len(sys.argv) != 3:
        print("Error: Incorrect number of  arguments.")
        print("Example: gen <num_regs> <filename>")
        return

    num_regs = int(sys.argv[1])
    if num_regs <= 0:
        print("Number of registers must be greater than 0")
        return
    
    filename = sys.argv[2]
    if not os.path.isfile(filename):
        print(f"Error: Cannot read input file '{filename}'.")
        return

    # Step 2: Run the Front-End (Scanner and Parser)
    p = Parser(filename)
    instructions = p.readIntermediateCode()
    live_vars = p.variables

    # Step 3: Run the Back-End (Liveness & Graph)
    graph = build_interference_graph(instructions, live_vars)

    # Step 4: Graph Coloring (Register Allocation)
    register_mapping = graph.colour_graph(num_registers=num_regs) 

    # Step 5: Code Generation
    # Pass the instructions and register mapping to build the assembly list
    asm_instructions = generate_assembly(instructions, register_mapping)

    # Step 6: The Final Output
    # Loop through your asm_instructions and print them to the console
    for asm in asm_instructions:
         print(asm)

# Step 7: Standard Execution Block
# This tells Python to run the main() function when we type "python main.py"
if __name__ == "__main__":
    main()