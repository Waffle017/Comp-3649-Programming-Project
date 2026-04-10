import os
import sys
import shutil
import subprocess

# TEMP switch for migration testing.
# True  -> force parser.hs
# False -> use parser.py
USE_HASKELL_PARSER = True

# TEMP switch for migration testing
# True  -> force allocator.hs
# False -> use allocator.py
USE_HASKELL_ALLOCATOR = True


def _backend_label(use_haskell, py_name, hs_name):
    if use_haskell:
        return f"Haskell ({hs_name})"
    return f"Python ({py_name})"

if not USE_HASKELL_PARSER:
    from parser import Parser
else:
    from instruction import Instruction

    class Parser:
        """
        Temporary parser adapter backed by parser.hs.
        Flip USE_HASKELL_PARSER to False to quickly go back to parser.py.
        """

        def __init__(self, filename):
            self.filename = filename
            self.output = []
            self.variables = []
            self.live_on_exit = []
            self.curr_token = None

        def _parse_operand(self, raw):
            if raw is None:
                return None
            if raw.lstrip("-").isdigit():
                return int(raw)
            return raw

        def _run_haskell_parser(self):
            parser_path = os.path.join(os.path.dirname(__file__), "parser.hs")
            haskell_runner = shutil.which("runghc") or shutil.which("runhaskell")

            if not haskell_runner or not os.path.isfile(parser_path):
                raise RuntimeError("Haskell parser runtime unavailable: install runghc/runhaskell.")

            result = subprocess.run(
                [haskell_runner, parser_path, self.filename],
                capture_output=True,
                text=True,
                check=False,
            )

            if result.returncode != 0:
                message = (result.stderr or "Parser failed.").strip()
                if "Missing 'live:' statement" in message:
                    raise SyntaxError(message)
                if "File not found" in message:
                    # Keep parity with parser.py behavior in this repo.
                    raise SyntaxError("Unexpected EOF: Missing 'live:' statement at the end of the file.")
                raise ValueError(message)

            return result.stdout.splitlines()

        def readIntermediateCode(self):
            self.output = []
            self.variables = []
            self.live_on_exit = []

            for line in self._run_haskell_parser():
                if not line.strip():
                    continue

                parts = line.split("\t")
                record_type = parts[0]

                if record_type == "INST" and len(parts) == 5:
                    _, dest, src1, op, src2 = parts
                    src1_parsed = self._parse_operand(src1)
                    src2_parsed = None if src2 == "-" else self._parse_operand(src2)
                    self.output.append(Instruction(dest, src1_parsed, op, src2_parsed))
                elif record_type == "LIVE" and len(parts) == 2:
                    self.live_on_exit.append(parts[1])
                elif record_type == "VAR" and len(parts) == 2:
                    self.variables.append(parts[1])

            return self.output
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

def _encode_instruction_for_haskell(instr):
    src2 = "-" if instr.src2 is None else str(instr.src2)
    return f"{instr.dest}\t{instr.src1}\t{instr.op}\t{src2}"

def _build_haskell_allocator_input(instructions, live_vars, num_regs):
    lines = [str(num_regs), " ".join(str(v) for v in live_vars)]
    lines.extend(_encode_instruction_for_haskell(instr) for instr in instructions)
    return "\n".join(lines) + "\n"

def build_register_mapping(instructions, live_vars, num_regs):
    allocator_path = os.path.join(os.path.dirname(__file__), "allocator.hs")
    haskell_runner = shutil.which("runghc") or shutil.which("runhaskell")

    if USE_HASKELL_ALLOCATOR:
        if not haskell_runner or not os.path.isfile(allocator_path):
            raise RuntimeError("Haskell allocator runtime unavailable: install runghc/runhaskell.")
        # Keep parity with allocator.py behavior (raises on undefined live vars).
        build_interference_graph(instructions, live_vars)
        payload = _build_haskell_allocator_input(instructions, live_vars, num_regs)
        result = subprocess.run(
            [haskell_runner, allocator_path],
            input=payload,
            capture_output=True,
            text=True,
            check=False
        )

        if result.returncode != 0:
            message = (result.stderr or "Allocator failed.").strip()
            raise RuntimeError(message)

        mapping = {}
        for line in result.stdout.splitlines():
            if not line.strip():
                continue
            var, _, value = line.partition("\t")
            mapping[var] = None if value == "spill" else int(value)
        return mapping

    # Python allocator path.
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
        print(f"Error: Cannot read input file '{filename}'.")
        return

    print(f"[backend] parser: {_backend_label(USE_HASKELL_PARSER, 'parser.py', 'parser.hs')}")
    print(f"[backend] allocator: {_backend_label(USE_HASKELL_ALLOCATOR, 'allocator.py', 'allocator.hs')}")

    # Step 2: Run the Front-End (Scanner and Parser)
    p = Parser(filename)
    instructions = p.readIntermediateCode()
    live_vars = p.live_on_exit

    # Step 3/4: Register Allocation via Haskell allocator
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