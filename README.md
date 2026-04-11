

## Running Both Implementations

This repo contains two implementations of the same compiler backend:

- `Haskell Solution/` (Haskell pipeline, executed with `runghc`)
- `Imperative Solution/` (Python pipeline, executed with `python3`)

All commands below should be run from the repository root unless noted otherwise.

### 1) Haskell Solution

#### Run the compiler on one input file
```sh
runghc "Haskell Solution" "Haskell Solution/Main.hs" <num_registers> "Haskell Solution/<input_file>.txt"
```

Example:
```sh
runghc -i"Haskell Solution" "Haskell Solution/Main.hs" 2 "Haskell Solution/test2_register_recycle.txt"
```

#### Run Haskell solution tests
```sh
cd "Haskell Solution"
python3 test_suite.py
```

### 2) Imperative Solution

#### Run the compiler on one input file
```sh
python3 "Imperative Solution/gen.py" <num_registers> "Imperative Solution/<input_file>.txt"
```

Example:
```sh
python3 "Imperative Solution/gen.py" 2 "Imperative Solution/test2_register_recycle.txt"
```

#### Run Imperative solution tests
```sh
cd "Imperative Solution"
python3 test_suite.py
```

### 3) Quick Comparison Workflow

Run both test suites:
```sh
cd "Haskell Solution" && python3 test_suite.py
cd "../Imperative Solution" && python3 test_suite.py
```

If you want to compare output for the same fixture manually, run:
```sh
runghc -i"Haskell Solution" "Haskell Solution/Main.hs" 2 "Haskell Solution/test12_memory_load.txt"
python3 "Imperative Solution/gen.py" 2 "Imperative Solution/test12_memory_load.txt"
```