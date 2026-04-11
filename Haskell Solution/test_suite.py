import subprocess
import tempfile
import unittest
from pathlib import Path


THIS_DIR = Path(__file__).resolve().parent
REPO_ROOT = THIS_DIR.parent
HASKELL_MAIN = THIS_DIR / "Main.hs"


def resolve_fixture(filename: str) -> Path:
    candidates = [
        THIS_DIR / filename,
        REPO_ROOT / "Imperative Solution" / filename,
        REPO_ROOT / filename,
    ]
    for path in candidates:
        if path.exists():
            return path
    raise FileNotFoundError(f"Fixture not found: {filename}")


def run_compiler_pipeline(filename: str, num_regs: int = 4) -> list[str]:
    fixture_path = resolve_fixture(filename)
    cmd = [
        "runghc",
        f"-i{THIS_DIR}",
        str(HASKELL_MAIN),
        str(num_regs),
        str(fixture_path),
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True, cwd=REPO_ROOT)
    combined = (proc.stdout or "") + (proc.stderr or "")

    if "spill occurred" in combined.lower():
        raise RuntimeError("spill occurred")

    if proc.returncode != 0:
        if "Missing 'live:' statement" in combined:
            raise SyntaxError(combined.strip())
        if "Parse error on line" in combined or "Invalid instruction format" in combined:
            raise SyntaxError(combined.strip())
        if "Undefined variable" in combined:
            raise NameError(combined.strip())
        raise RuntimeError(combined.strip() or "Compiler pipeline failed.")

    return [ln.strip() for ln in proc.stdout.splitlines() if ln.strip()]


class TestHaskellCompilerBackEnd(unittest.TestCase):
    def test_spill(self):
        with self.assertRaises(RuntimeError):
            run_compiler_pipeline("test1_spill.txt", num_regs=2)

    def test_register_recycle(self):
        asm = run_compiler_pipeline("test2_register_recycle.txt", num_regs=2)
        self.assertTrue(len(asm) > 0)

    def test_ghost_var(self):
        asm = run_compiler_pipeline("test4_ghost_var.txt", num_regs=2)
        self.assertTrue(len(asm) > 0)

    def test_long_lived(self):
        asm = run_compiler_pipeline("test5_long_lived.txt", num_regs=2)
        self.assertTrue(len(asm) > 0)

    def test_reassignment(self):
        asm = run_compiler_pipeline("test6_reassignment.txt", num_regs=1)
        self.assertTrue(len(asm) > 0)

    def test_independent_chains(self):
        asm = run_compiler_pipeline("test7_independent_chains.txt", num_regs=2)
        self.assertTrue(len(asm) > 0)

    def test_self_reference(self):
        asm = run_compiler_pipeline("test8_self_reference.txt", num_regs=1)
        self.assertTrue(len(asm) > 0)

    def test_live_only(self):
        asm = run_compiler_pipeline("test9_live_only.txt", num_regs=2)
        self.assertTrue(len(asm) > 0)

    def test_all_literals(self):
        asm = run_compiler_pipeline("test10_all_literals.txt", num_regs=2)
        self.assertTrue(len(asm) > 0)

    def test_chain_assignments(self):
        asm = run_compiler_pipeline("test11_chain_assignments.txt", num_regs=1)
        self.assertTrue(len(asm) > 0)

    def test_memory_load(self):
        asm = run_compiler_pipeline("test12_memory_load.txt", num_regs=2)
        load_count = 0
        for line in asm:
            clean_line = line.replace(" ", "").replace("\t", "")
            if "MOVa" in clean_line:
                load_count += 1
        self.assertEqual(load_count, 1, f"'a' should be loaded once, but was loaded {load_count} times.")

    def test_messy_input(self):
        with self.assertRaises(SyntaxError):
            run_compiler_pipeline("test13_messy_input.txt", num_regs=2)

    def test_long_variable_names(self):
        var_1 = "super_duper_extra_amazing_long_variable_name"
        var_2 = "super_duper_extra_amazing_long_variable_name_the_second"
        content = "\n".join(
            [
                f"{var_1} = 10 + 20",
                f"{var_2} = {var_1} + 1",
                f"live: {var_2}",
            ]
        )
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write(content)
            path = Path(f.name)
        try:
            asm = run_compiler_pipeline(str(path), num_regs=2)
            asm_string = "\n".join(asm)
            self.assertIn(var_1, asm_string)
            self.assertIn(var_2, asm_string)
        finally:
            path.unlink(missing_ok=True)

    def test_vars_with_nums(self):
        content = "\n".join(
            [
                "var1 = 10 + 20",
                "var2 = var1 + 3",
                "var3 = var2 + var1",
                "live: var3",
            ]
        )
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write(content)
            path = Path(f.name)
        try:
            asm = run_compiler_pipeline(str(path), num_regs=2)
            self.assertIn("var3", "\n".join(asm))
        finally:
            path.unlink(missing_ok=True)

    def test_missing_live_statement(self):
        content = "\n".join(["a = 10 + 20", "b = a * 2", "c = b - 5"])
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write(content)
            path = Path(f.name)
        try:
            with self.assertRaises(SyntaxError) as context:
                run_compiler_pipeline(str(path), num_regs=2)
            self.assertIn("Missing 'live:' statement", str(context.exception))
        finally:
            path.unlink(missing_ok=True)


if __name__ == "__main__":
    unittest.main()
import subprocess
import tempfile
import unittest
from pathlib import Path


THIS_DIR = Path(__file__).resolve().parent
REPO_ROOT = THIS_DIR.parent
HASKELL_MAIN = THIS_DIR / "Main.hs"


def resolve_fixture(filename: str) -> Path:
    candidates = [
        THIS_DIR / filename,
        REPO_ROOT / "Imperative Solution" / filename,
        REPO_ROOT / filename,
    ]
    for path in candidates:
        if path.exists():
            return path
    raise FileNotFoundError(f"Fixture not found: {filename}")


def run_compiler_pipeline(filename: str, num_regs: int = 4) -> list[str]:
    fixture_path = resolve_fixture(filename)
    cmd = [
        "runghc",
        f"-i{THIS_DIR}",
        str(HASKELL_MAIN),
        str(num_regs),
        str(fixture_path),
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True, cwd=REPO_ROOT)
    combined = (proc.stdout or "") + (proc.stderr or "")

    if "spill occurred" in combined.lower():
        raise RuntimeError("spill occurred")

    if proc.returncode != 0:
        if "Missing 'live:' statement" in combined:
            raise SyntaxError(combined.strip())
        if "Parse error on line" in combined or "Invalid instruction format" in combined:
            raise SyntaxError(combined.strip())
        if "Undefined variable" in combined:
            raise NameError(combined.strip())
        raise RuntimeError(combined.strip() or "Compiler pipeline failed.")

    asm_lines = [ln.strip() for ln in proc.stdout.splitlines() if ln.strip()]
    return asm_lines


class TestHaskellCompilerBackEnd(unittest.TestCase):
    def test_spill(self):
        with self.assertRaises(RuntimeError):
            run_compiler_pipeline("test1_spill.txt", num_regs=2)

    def test_register_recycle(self):
        asm = run_compiler_pipeline("test2_register_recycle.txt", num_regs=2)
        self.assertTrue(len(asm) > 0)

    def test_ghost_var(self):
        asm = run_compiler_pipeline("test4_ghost_var.txt", num_regs=2)
        self.assertTrue(len(asm) > 0)

    def test_long_lived(self):
        asm = run_compiler_pipeline("test5_long_lived.txt", num_regs=2)
        self.assertTrue(len(asm) > 0)

    def test_reassignment(self):
        asm = run_compiler_pipeline("test6_reassignment.txt", num_regs=1)
        self.assertTrue(len(asm) > 0)

    def test_independent_chains(self):
        asm = run_compiler_pipeline("test7_independent_chains.txt", num_regs=2)
        self.assertTrue(len(asm) > 0)

    def test_self_reference(self):
        asm = run_compiler_pipeline("test8_self_reference.txt", num_regs=1)
        self.assertTrue(len(asm) > 0)

    def test_live_only(self):
        asm = run_compiler_pipeline("test9_live_only.txt", num_regs=2)
        self.assertTrue(len(asm) > 0)

    def test_all_literals(self):
        asm = run_compiler_pipeline("test10_all_literals.txt", num_regs=2)
        self.assertTrue(len(asm) > 0)

    def test_chain_assignments(self):
        asm = run_compiler_pipeline("test11_chain_assignments.txt", num_regs=1)
        self.assertTrue(len(asm) > 0)

    def test_memory_load(self):
        asm = run_compiler_pipeline("test12_memory_load.txt", num_regs=2)
        load_count = 0
        for line in asm:
            clean_line = line.replace(" ", "").replace("\t", "")
            if "MOVa" in clean_line:
                load_count += 1
        self.assertEqual(load_count, 1, f"'a' should be loaded once, but was loaded {load_count} times.")

    def test_messy_input(self):
        with self.assertRaises(SyntaxError):
            run_compiler_pipeline("test13_messy_input.txt", num_regs=2)

    def test_long_variable_names(self):
        var_1 = "super_duper_extra_amazing_long_variable_name"
        var_2 = "super_duper_extra_amazing_long_variable_name_the_second"
        content = "\n".join(
            [
                f"{var_1} = 10 + 20",
                f"{var_2} = {var_1} + 1",
                f"live: {var_2}",
            ]
        )
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write(content)
            path = Path(f.name)
        try:
            asm = run_compiler_pipeline(str(path), num_regs=2)
            asm_string = "\n".join(asm)
            self.assertIn(var_1, asm_string)
            self.assertIn(var_2, asm_string)
        finally:
            path.unlink(missing_ok=True)

    def test_vars_with_nums(self):
        content = "\n".join(
            [
                "var1 = 10 + 20",
                "var2 = var1 + 3",
                "var3 = var2 + var1",
                "live: var3",
            ]
        )
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write(content)
            path = Path(f.name)
        try:
            asm = run_compiler_pipeline(str(path), num_regs=2)
            self.assertIn("var3", "\n".join(asm))
        finally:
            path.unlink(missing_ok=True)

    def test_missing_live_statement(self):
        content = "\n".join(
            [
                "a = 10 + 20",
                "b = a * 2",
                "c = b - 5",
            ]
        )
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write(content)
            path = Path(f.name)
        try:
            with self.assertRaises(SyntaxError) as context:
                run_compiler_pipeline(str(path), num_regs=2)
            self.assertIn("Missing 'live:' statement", str(context.exception))
        finally:
            path.unlink(missing_ok=True)


if __name__ == "__main__":
    unittest.main()