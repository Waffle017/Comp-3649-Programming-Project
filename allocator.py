'''
Takes the list of instructions from parser
and a live_variables list from the last line (live: d for example)
will then scan the file from end to start to see which variables are live at the same time

example use in main:
p = Parser(filename)
p.parse()
graph = build_interference_graph(p.instructions, p.live_variables)
graph.graph_print()
'''

class InterferenceGraph:
    def __init__(self):
        # Using dictionaries to hold conflicting variables
        # Key: the variable name, Value: set of variables it conflicts with
        self.conflicts_list = {}

    def add_node(self, var):
        # If the variable isn't already in the list, add an empty node to the graph/dictionary entry
        if var not in self.conflicts_list:
            self.conflicts_list[var] = set()

    def ensure_variable(object):
        # Helper function to make sure we are only reading variables
        return type(object) is str
    
    def add_edge(self, var1, var2):
        if (var1 != var2) and (var1.ensure_variable) and (var2.ensure_variable):
            self.add_node(self, var1)
            self.add_node(self, var2)
            self.conflicts_list[var1].add[var2]
            self.conflicts_list[var2].add[var1]

    #def print_graph(self);

def build_interference_graph(instructions, live_on_exit):
    '''
    Docstring for build_interference_graph
    
    :param instructions: List of all instructions from parser
    :param live_on_exit: List of variables live at the end
    '''
    graph = InterferenceGraph()

    # Initialize live list with variables that were live
    current_live = list(live_on_exit)

    # Add variables that are live on exit to graph
    for variable in current_live:
        dest_var = instruction.dest

    # Start loop for backwards iteration
    for instruction in reversed(instructions):

        # Find destination variable
        dest = instruction.dest

        # Handle Assignment (dest = ...)
        # add edges for destination variable with current live variables
        for live_variable in current_live:
            graph.add_edge(dest, live_variable)
            
            # kill the dest variable on assignment line IF it is in the current_live list
        if dest in current_live:
            current_live.remove(dest)

            # Even if no edges, add to graph
        graph.add_node(dest)

        # Handle binary operations and unary negations

        if graph.ensure_variable(instruction.src1):
            current_live.add(instruction.src1)
            graph.add_node(instruction.src1)

        # Check for source 2
        if instruction.src2 and graph.ensure_variable(instruction.src2):
            current_live.add(instruction.src2)
            graph.add_node(instruction.src2)
    return graph 