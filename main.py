
import sys
from parser import Parser
from allocator import build_interference_graph
from instruction import Asm_Instruction 

# Step 6: Code Generation function (Stub to fill in later)
def generate_assembly(intermediate_instructions, register_allocation):
    asm_output = []
    
    # You will write the loop here to convert the 3-address 
    # instructions into a list of Asm_Instruction objects
    
    return asm_output

def main():
    # Step 1: Check for command-line arguments
    if len(sys.argv) < 2:
        print("Error: Please provide an input file.")
        print("Example: python main.py programpara.txt")
        return
    
    filename = sys.argv[1]

    # Step 2: Run the Front-End (Scanner and Parser)
    p = Parser(filename)
    instructions = p.readIntermediateCode()
    live_vars = p.variables

    # Step 3: Run the Back-End (Liveness & Graph)
    graph = build_interference_graph(instructions, live_vars)

    # Step 4: Graph Coloring (Register Allocation)
    register_mapping = graph.colour_graph(num_registers=4) 
    graph.graph_print()

    # Step 5: Code Generation
    # Pass the instructions and register mapping to build the assembly list
    # asm_instructions = generate_assembly(instructions, register_mapping)

    # Step 6: The Final Output
    # Loop through your asm_instructions and print them to the console
    # for asm in asm_instructions:
    #     print(asm)

# Step 7: Standard Execution Block
# This tells Python to run the main() function when we type "python main.py"
if __name__ == "__main__":
    main()