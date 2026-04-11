from scanner import Scanner
from gen import Parser


if __name__ == "__main__":
    print("=== SCANNER TEST ===") #test scanner
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
        instructions = parser.readIntermediateCode()
        
        print("\nParsed Instructions:")
        for i, instruction in enumerate(instructions):
            print(f"Instruction {i+1}: {instruction}")

        print("\nVariables found:")
        print(parser.variables)
        
    except Exception as e:
        print(f"Error occurred: {e}")
        import traceback
        traceback.print_exc()
