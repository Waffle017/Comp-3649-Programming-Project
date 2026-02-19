#this will test the scanner.py file
from scanner import Scanner, Token
import os

def test_scanner():
    # Create a test file with the provided code
    test_filename = "test_scanner_input.txt"
    test_code = """a = a + 1
t1 = a * 4
t2 = t1 + 1
t3 = a * 3
b = t2 - t3
t4 = b / 2
d = c + t4"""
    
    
    with open(test_filename, 'w') as f: #write to test file
        f.write(test_code)
    
    # Create scanner and tokenize
    scanner = Scanner(test_filename)
    tokens = []
    
    print(f"Testing scanner with code:{test_code} \n Tokens generated:")
   
    while True:
        token = scanner.get_token()
        if token is None:
            break
        tokens.append(token)
        print(token)
    
    print(f"Total tokens: {len(tokens)}")
    
    
    # Verify expected tokens
    expected_tokens = [
        ('VAR', 'a'),
        ('ASSIGN', '='),
        ('VAR', 'a'),
        ('PLUS', '+'),
        ('INT', 1),
        ('NEWLINE', '\n'),
        ('VAR', 't1'),
        ('ASSIGN', '='),
        ('VAR', 'a'),
        ('MUL', '*'),
        ('INT', 4),
        ('NEWLINE', '\n'),
        ('VAR', 't2'),
        ('ASSIGN', '='),
        ('VAR', 't1'),
        ('PLUS', '+'),
        ('INT', 1),
        ('NEWLINE', '\n'),
        ('VAR', 't3'),
        ('ASSIGN', '='),
        ('VAR', 'a'),
        ('MUL', '*'),
        ('INT', 3),
        ('NEWLINE', '\n'),
        ('VAR', 'b'),
        ('ASSIGN', '='),
        ('VAR', 't2'),
        ('MINUS', '-'),
        ('VAR', 't3'),
        ('NEWLINE', '\n'),
        ('VAR', 't4'),
        ('ASSIGN', '='),
        ('VAR', 'b'),
        ('DIV', '/'),
        ('INT', 2),
        ('NEWLINE', '\n'),
        ('VAR', 'd'),
        ('ASSIGN', '='),
        ('VAR', 'c'),
        ('PLUS', '+'),
        ('VAR', 't4'),
        ('NEWLINE', '\n'),  # Final newline from file
    ]
    # right amount of tokens
    if len(tokens) != len(expected_tokens):
        print(f" Wrong number of tokens: got {len(tokens)}, expected {len(expected_tokens)}")
        all_match = False
    else:
        all_match = True
        for i in range(len(tokens)):
            expected_type, expected_value = expected_tokens[i]
            if tokens[i].type != expected_type or tokens[i].value != expected_value: #checks if token matches expected token
                print(f" Token {i}: expected {expected_type}({repr(expected_value)}), got {tokens[i]}")
                all_match = False
        
        if all_match:
            print("All tokens match!")
    
    # remove test file for good code practice
    if os.path.exists(test_filename):
        os.remove(test_filename)
    return tokens
    
def test_missing_live_error():
    
    test_filename = "test_missing_live.txt"
    # Test code WITHOUT 'live:' statement - this should be an error
    test_code = """a = a + 1
t1 = a * 4
b = t1 + 2"""
    
    try:
        with open(test_filename, 'w') as f:
            f.write(test_code)
        
        # Create scanner and tokenize
        scanner = Scanner(test_filename)
        tokens = []
        
       
        while True:
            token = scanner.get_token()
            if token is None:
                break
            tokens.append(token)

        has_live = False
        for token in tokens:
            if token.type == 'END' and token.value == 'live':
                has_live = True
                break       
        if  has_live == False:
            print(" ERROR: Missing 'live:' statement")
        
        # Clean up test file
        if os.path.exists(test_filename):
            os.remove(test_filename)
        
        return has_live
    
    except Exception as e:
        print(f"Something went wrong: {e}")
        # Clean up test file even on error
        if os.path.exists(test_filename):
            os.remove(test_filename)
        return False


if __name__ == "__main__":
    test_scanner()
    test_missing_live_error()
   
