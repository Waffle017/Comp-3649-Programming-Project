import unittest
import os
import sys

# Ensure the current directory is in the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from allocator import build_interference_graph
from gen import Parser, build_register_mapping, generate_assembly

def run_compiler_pipeline(filepath, num_regs=4):
    """
    Helper function to run the compiler pipeline and return stringified assembly.
    """
    # 1. Parse
    p = Parser(filepath)
    instructions = p.readIntermediateCode()
    live_vars = p.live_on_exit

    # 2. Allocate Registers
    register_mapping = build_register_mapping(instructions, live_vars, num_regs)

    # 3. Generate Assembly
    asm_instructions = generate_assembly(instructions, register_mapping, live_vars)
    
    # Return as a list of strings for easy comparison
    return [str(asm) for asm in asm_instructions]

class TestCompilerBackEnd(unittest.TestCase):
    
    def test_spill(self):
        "Test that the compiler raises a RuntimeError when a spill occurs"
        with self.assertRaises(RuntimeError):
            run_compiler_pipeline("test1_spill.txt", num_regs=2)  # Two Registers for a three register problem.

    def test_register_recycle(self):
        "Test that registers are recycled when a register becomes free"
        try:
            asm = run_compiler_pipeline("test2_register_recycle.txt", num_regs=2)
        except RuntimeError as e:
            self.fail("Register recycling failed, all registers were not recycled properly: " + str(e))         

    def test_live_on_entry(self):
        "Tests that the backward liveness scan correctly identifies variables that are live on entry (used before being defined in the block)."
        p = Parser('test3_live_on_entry.txt')
        instructions = p.readIntermediateCode()
        live_vars = p.live_on_exit

        graph = build_interference_graph(instructions, live_vars)
        
        self.assertTrue(hasattr(graph, 'live_on_entry'), "Graph should store live_on_entry property.")
        
        # 'a' and 'b' are used without being defined, so they are live on entry
        self.assertIn('a', graph.live_on_entry)
        self.assertIn('b', graph.live_on_entry)
        
        # 'c' and 't1' are defined inside the block, so they are NOT live on entry
        self.assertNotIn('c', graph.live_on_entry)
        self.assertNotIn('t1', graph.live_on_entry)

    def test_ghost_var(self):
        "Tests that variables that are not used are not added to the interference graph and do not cause spills."
        p = Parser('test4_ghost_var.txt')
        instructions = p.readIntermediateCode()
        live_vars = p.live_on_exit

        graph = build_interference_graph(instructions, live_vars)

        self.assertIn('ghost', graph.conflicts_list)

        self.assertIn('a', graph.conflicts_list['ghost'])

        self.assertNotIn('b', graph.conflicts_list['ghost'])

        try:
            asm = run_compiler_pipeline("test4_ghost_var.txt", num_regs=2)
            self.assertTrue(len(asm) > 0)
        except RuntimeError as e:
            self.fail("Ghost variable handling failed, unexpected spill: " + str(e))

    def test_long_lived(self):
        "Tests that one long-lived variable correctly holds a single register while other short-lived variables safely share a single register."
        # Parse and build graph to inspect the interference edges
        p = Parser('test5_long_lived.txt')
        instructions = p.readIntermediateCode()
        live_vars = p.live_on_exit

        graph = build_interference_graph(instructions, live_vars)
        
        # 'long' should conflict with all the short-lived variables
        short_vars = ['s1', 't1', 's2', 't2', 's3']
        for var in short_vars:
            self.assertIn(var, graph.conflicts_list['long'], f"'long' should conflict with {var}")
            
        # Short-lived variables should NOT conflict with each other
        self.assertNotIn('s2', graph.conflicts_list['s1'])
        self.assertNotIn('s3', graph.conflicts_list['t1'])

        try:
            asm = run_compiler_pipeline("test5_long_lived.txt", num_regs=2)
            self.assertTrue(len(asm) > 0)
        except RuntimeError as e:
            self.fail(f"Long-lived variable test failed, unexpected spill: {e}")

    def test_reassignment(self):
        "Tests that a single variable can be repeatedly assigned using only one register."

        p = Parser('test6_reassignment.txt')
        instructions = p.readIntermediateCode()
        live_vars = p.live_on_exit

        graph = build_interference_graph(instructions, live_vars)

        self.assertIn('a', graph.conflicts_list)
        self.assertEqual(len(graph.conflicts_list['a']), 0, 'a should have no conflicts')

        # Pipeline should succeed using one registers
        try:
            asm = run_compiler_pipeline("test6_reassignment.txt", num_regs=1)
            self.assertTrue(len(asm) > 0)
        except RuntimeError as e:
            self.fail(f"Reassignment test failed, unexpected spill: {e}")

    def test_independent_chains(self):
        "Tests that two independent chains of variables can safely share registers without causing spills."

        p = Parser('test7_independent_chains.txt')
        instructions = p.readIntermediateCode()
        live_vars = p.live_on_exit

        graph = build_interference_graph(instructions, live_vars)

        # Overlapping conflicts between chains
        self.assertIn('x', graph.conflicts_list['a'], "'a' should conflict with 'x'")
        self.assertIn('b', graph.conflicts_list['x'], "'b' should conflict with 'x'")
        self.assertIn('y', graph.conflicts_list['b'], "'b' should conflict with 'y'")

        # No cross-chain conflicts
        self.assertNotIn('c', graph.conflicts_list['a'], "'a' should NOT conflict with 'c'")
        self.assertNotIn('z', graph.conflicts_list['x'], "'x' should NOT conflict with 'z'")

        # Pipeline should succeed using two registers
        try:
            asm = run_compiler_pipeline("test7_independent_chains.txt", num_regs=2)
            self.assertTrue(len(asm) > 0)
        except RuntimeError as e:
            self.fail(f"Independent chains test failed, unexpected spill: {e}")

    def test_self_reference(self):
        "Tests that a variable that references itself does not cause a spill and is allocated to a single register."

        p = Parser('test8_self_reference.txt')
        instructions = p.readIntermediateCode()
        live_vars = p.live_on_exit

        graph = build_interference_graph(instructions, live_vars)

        self.assertIn('a', graph.conflicts_list)
        self.assertEqual(len(graph.conflicts_list['a']), 0, 'a should have no conflicts')

        # Pipeline should succeed using one register
        try:
            asm = run_compiler_pipeline("test8_self_reference.txt", num_regs=1)
            self.assertTrue(len(asm) > 0)
        except RuntimeError as e:
            self.fail(f"Self-reference test failed, unexpected spill: {e}")

    def test_live_only(self):
        "Tests that code that only uses live on entry and live on exit creates no local variables."

        p = Parser('test9_live_only.txt')
        instructions = p.readIntermediateCode()
        live_vars = p.live_on_exit

        graph = build_interference_graph(instructions, live_vars)

        # x and y should be live on entry
        self.assertIn('x', graph.live_on_entry, "'x' should be live on entry.")
        self.assertIn('y', graph.live_on_entry, "'y' should be live on entry.")

        # There should be no other variables
        self.assertEqual(len(graph.conflicts_list), 2, "There should only be 2 variables in the graph.")

        # x and y must conflict
        self.assertIn('y', graph.conflicts_list['x'], "'x' and 'y' must conflict.")

        # Should only use two registers
        try:
            asm = run_compiler_pipeline("test9_live_only.txt", num_regs=2)
            self.assertTrue(len(asm) > 0)
        except RuntimeError as e:
            self.fail(f"Live-only test failed, unexpected spill: {e}")

    def test_all_literals(self):
        "Tests that the program does not add literals to the interference graph and does not attempt to allocate registers for them."

        p = Parser('test10_all_literals.txt')
        instructions = p.readIntermediateCode()
        live_vars = p.live_on_exit

        graph = build_interference_graph(instructions, live_vars)

        # Only variables 'a' and 'b' should be in the grpah
        self.assertIn('a', graph.conflicts_list)
        self.assertIn('b', graph.conflicts_list)
        self.assertEqual(len(graph.conflicts_list), 2, "Only 'a' and 'b' should be in the graph.")

        # Ensure that 'a' and 'b' conflict
        self.assertIn('b', graph.conflicts_list['a'], "'a' and 'b' should conflict.")

        # Pipeline should only use 2 registers
        try:
            asm = run_compiler_pipeline("test10_all_literals.txt", num_regs=2)
            self.assertTrue(len(asm) > 0)
        except RuntimeError as e:
            self.fail(f"All literals test failed, unexpected spill: {e}")

    def test_chain_assignments(self):
        "Tests is the compiler can recognize when a chain of assignments don't overlap and can be allocated one register."

        p = Parser('test11_chain_assignments.txt')
        instructions = p.readIntermediateCode()
        live_vars = p.live_on_exit

        graph = build_interference_graph(instructions, live_vars)

        # Variables should have no conflicts
        chain_vars = ['a', 'b', 'c', 'd', 'e']
        for var in chain_vars:
            self.assertIn(var, graph.conflicts_list)
            self.assertEqual(len(graph.conflicts_list[var]), 0, f"{var} should have no conflicts")
        
        # Pipline should only use 1 register
        try:
            asm = run_compiler_pipeline("test11_chain_assignments.txt", num_regs=1)
            self.assertTrue(len(asm) > 0)
        except RuntimeError as e:
            self.fail(f"Chain assignments test failed, unexpected spill: {e}")
    
    def test_memory_load(self):
        "Tests that the compiler correctly loads a variable into a register, and does not attempt another load that has been loaded before."

        try:
            asm = run_compiler_pipeline("test12_memory_load.txt", num_regs=2)
            self.assertTrue(len(asm) > 0)

            asm_string = "\n".join(asm)

            # Check that 'a' is loaded, but only once
            load_count = 0
            for line in asm:
                clean_line = line.replace(" ", "").replace("\t", "")
                if "MOVa" in clean_line:
                    load_count += 1
            
            self.assertEqual(load_count, 1, f"'a' should be loaded exactly once, but was loaded {load_count} times.")
        except RuntimeError as e:
            self.fail(f"Memory load test failed, unexpected spill: {e}")

    def test_messy_input(self):
        "Tests that the scanner can ignore whitespace and continue making assembly instructions correctly."
        try:
            p = Parser('test13_messy_input.txt')
            instructions = p.readIntermediateCode()
            live_vars = p.live_on_exit

            # Verify that the parser found 3 instructions
            self.assertEqual(len(instructions), 3, "Parser should find 3 instructions.")

            self.assertIn('c', live_vars, "'c' should be live on exit.")

            # Pipeline should succeed using two registers
            asm = run_compiler_pipeline("test13_messy_input.txt", num_regs=2)
            self.assertTrue(len(asm) > 0)
        
        except RuntimeError as e:
            self.fail(f"Messy input test failed, unexpected spill: {e}")

    def test_long_variable_names(self):
        "Tests that the compiler can handle long variable names without issues."

        var_1 = "super_duper_extra_amazing_long_variable_name"
        var_2 = "super_duper_extra_amazing_long_variable_name_the_second"

        try:
            p = Parser('test14_long_variable_names.txt')
            instructions = p.readIntermediateCode()
            live_vars = p.live_on_exit

            # Check that the long variable names are in the graph
            self.assertIn(var_2, live_vars, "Long variable names should be handled correctly.")

            asm = run_compiler_pipeline("test14_long_variable_names.txt", num_regs=2)
            self.assertTrue(len(asm) > 0)

            asm_string = "\n".join(asm)
            self.assertTrue(var_1 in asm_string, f"Assembly should contain the string: {var_1}")
            self.assertTrue(var_2 in asm_string, f"Assembly should contain the string: {var_2}")

        except RuntimeError as e:
            self.fail(f"Long variable names test failed, unexpected error: {e}")

    def test_vars_with_nums(self):
        "Tests that the compiler can handle variable names that contain numbers without issues."

        try:
            p = Parser('test15_vars_with_nums.txt')
            instructions = p.readIntermediateCode()
            live_vars = p.live_on_exit

            graph = build_interference_graph(instructions, live_vars)

            # Check that the variable names with numbers are in the graph
            self.assertIn('var3', graph.conflicts_list)
            self.assertIn('var2', graph.conflicts_list)

            asm = run_compiler_pipeline("test15_vars_with_nums.txt", num_regs=2)
            self.assertTrue(len(asm) > 0)

            asm_string = "\n".join(asm)
            self.assertTrue("var3" in asm_string, "Assembly should contain the variable 'var3'")

        except RuntimeError as e:
            self.fail(f"Variable names with numbers test failed, unexpected error: {e}")

    def test_missing_live_statement(self):
        "Tests that the compiler can handle a missing live statement without crashing, and that it treats all variables as not live on exit."

        with self.assertRaises(SyntaxError) as context:
            run_compiler_pipeline("test16_missing_live_statement.txt", num_regs=2)

        self.assertTrue("Missing 'live:' statement" in str(context.exception),
                        "Compiler should output a syntax error.")
        
    def test_undefined_live_variable(self):
        "Tests that the compiler raises an error when a variable listed in the live statement is not defined in the code."

        with self.assertRaises(NameError) as context:
            run_compiler_pipeline("test17_undefined_live.txt", num_regs=2)

        self.assertTrue("undefined" in str(context.exception), 
                        "Compiler should name the specific undefined variable.")
        self.assertTrue("Undefined variable" in str(context.exception),
                        "Compiler should declare the variable undefined")


if __name__ == '__main__':
    unittest.main()