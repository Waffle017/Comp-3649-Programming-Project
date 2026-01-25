from xxlimited import Null


class Instruction:
    def line_initiale(line, string, destination, src1, operator, src2):
        # we initialize here guys like line.string = read input
        pass




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
                    lines.append("")  # Add empty string between each line to mark new line
    except FileNotFoundError:
        print(f"File not found")
        return Null #idk if its NULL or Null or None doesn't matter much
    
    return lines



lines = readIn("programpara.txt") # reads in the file, can be changed depending on txt file name
print(lines) #error checking 