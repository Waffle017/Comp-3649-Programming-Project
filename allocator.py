'''
Builds an interference graph from instructions and live-on-exit,
then can colour it for register allocation.

Usage:
  graph = build_interference_graph(p.instructions, p.live_variables)
  graph.colour_graph()
  graph.graph_print()
'''

class InterferenceGraph:
    def __init__(self):
        self.conflicts_list = {}  # var -> set of vars it conflicts with
        self.colouring = {}       # var -> register number (after colour_graph)

    def add_node(self, var):
        if var not in self.conflicts_list:
            self.conflicts_list[var] = set()

    def add_edge(self, var1, var2):
        if var1 == var2 or type(var1) is not str or type(var2) is not str:
            return
        self.add_node(var1)
        self.add_node(var2)
        self.conflicts_list[var1].add(var2)
        self.conflicts_list[var2].add(var1)

    def colour_graph(self, num_registers=None):
        '''Assign each variable a register (colour) so no two neighbours share one.'''
        self.colouring = {} #reset colours
        for var in self.conflicts_list: # for each variable in the conflicts list
            used = {self.colouring[n]  #look at the colours of the neighbours
            for n in self.conflicts_list[var] #for each neighbour
            if n in self.colouring} #if the neighbour is in the colouring

            colour = 0 #start with colour 0
            while colour in used: #while the colour is used
                colour += 1
            if num_registers is not None and colour >= num_registers: #if the colour is greater than the number of registers set to none
                colour = None  # spillage
            self.colouring[var] = colour #set the colour of the variable
        return self.colouring

    def graph_print(self):
        print("Interference graph:")
        for var, neighbors in sorted(self.conflicts_list.items()):
            print(f"  {var}: {sorted(neighbors)}")
        if self.colouring:
            print("Colouring:")
            for var in sorted(self.colouring):
                r = self.colouring[var]
                if r is not None:
                    print(f"  {var} -> r{r}")
                else:
                    print(f"  {var} -> spill")


def build_interference_graph(instructions, live_on_exit):
    ''' 
    Docstring for build_interference_graph
    
    :param instructions: List of all instructions from parser
    :param live_on_exit: List of variables live at the end
    '''
    graph = InterferenceGraph()

    # Initialize live list with variables that were live
    current_live = list(live_on_exit)

    for var in current_live:
        graph.add_node(var)

    # Start loop for backwards iteration
    for instruction in reversed(instructions):

        # Find destination variable
        dest = instruction.dest
        for live_var in current_live:
            graph.add_edge(dest, live_var)
        if dest in current_live:
            current_live.remove(dest)
        graph.add_node(dest)

        if type(instruction.src1) is str:
            current_live.add(instruction.src1)
            graph.add_node(instruction.src1)
        if instruction.src2 and type(instruction.src2) is str:
            current_live.add(instruction.src2)
            graph.add_node(instruction.src2)

    return graph
