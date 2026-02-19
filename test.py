from scanner import Scanner
from parser import Parser



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

        print("\nVariables found:")
        print(parser.variables)
        
    except Exception as e:
        print(f"Error occurred: {e}")
        import traceback
        traceback.print_exc()
