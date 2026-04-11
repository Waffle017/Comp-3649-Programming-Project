import os
import sys
from parser import Parser
from allocator import build_interference_graph
from instruction import Asm_Instruction 

# Step 6: Code Generation function (Stub to fill in later)
def generate_assembly(intermediate_instructions, register_mapping, live_vars):
    asm_output = []
    loaded_vars = set() # Construct a set to keep track of variables already loaded

    spilled_vars = [var for var, reg in register_mapping.items() if reg is None]
    if spilled_vars:
        raise RuntimeError("Error: Spill detected, insufficient registers)")

    def is_real_var(op):
        return isinstance(op, str) and not (op.startswith('t') and len(op) > 1 and op[1:].isdigit())

    def format_operand(op):
        # Numbers become immediates: 1 -> #1
        if isinstance(op, int):
            return f"#{op}"
        
        # Variables in registers: a -> R0, etc.
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

        # Checks loaded_vars for any memory of a variable, if has not been, load it into a register first
        for src in [instr.src1, instr.src2]:
            if is_real_var(src) and src not in loaded_vars:
                src_reg = format_operand(src)
                asm_output.append(Asm_Instruction("MOV", src_reg, src))
                loaded_vars.add(src)

        dest_reg = format_operand(instr.dest)
        src1_formatted = format_operand(instr.src1)

        # Move source 1 into destination register
        if dest_reg != src1_formatted:
            asm_output.append(Asm_Instruction("MOV", dest_reg, src1_formatted))

        if instr.op in opcode_map and instr.src2 is not None:
            src2_formatted = format_operand(instr.src2)
            opcode = opcode_map[instr.op]
            asm_output.append(Asm_Instruction(opcode, dest_reg, src2_formatted))

        # Add the destination variable to loaded_vars to indicate it's now in a register
        if is_real_var(instr.dest):
            loaded_vars.add(instr.dest)

    for var in live_vars:
        if is_real_var(var) and var in register_mapping:
            reg_name = f"R{register_mapping[var]}"
            asm_output.append(Asm_Instruction("MOV", var, reg_name))

    return asm_output

def build_register_mapping(instructions, live_vars, num_regs):
    graph = build_interference_graph(instructions, live_vars)
    return graph.colour_graph(num_registers=num_regs)

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
        candidate = os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)
        if os.path.isfile(candidate):
            filename = candidate
        else:
            print(f"Error: Cannot read input file '{filename}'.")
            return

    # Step 2: Run the Front-End (Scanner and Parser)
    p = Parser(filename)
    instructions = p.readIntermediateCode()
    live_vars = p.live_on_exit

    # Step 3/4: Register Allocation via Python allocator
    register_mapping = build_register_mapping(instructions, live_vars, num_regs)

    # Step 5: Code Generation
    # Pass the instructions and register mapping to build the assembly list
    asm_instructions = generate_assembly(instructions, register_mapping, live_vars)

    # Step 6: The Final Output
    # Loop through your asm_instructions and print them to the console
    for asm in asm_instructions:
         print(asm)

# Step 7: Standard Execution Block
# This tells Python to run the main() function when we type "python main.py"
if __name__ == "__main__":
    main()