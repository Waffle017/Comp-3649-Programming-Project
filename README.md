# Register Allocation Program for a Simple Compiler

## Developing and Contributing
### Pull Requests
- Before doing any changes, make sure we pull newest changes from main
```sh
git checkout main
git pull origin main
```
- For any new feature/change, we create a new branch:
- We name the branch in the following format:
  - **category/name**
  - for example:
    - feat/graph-implementation
    - fix/linked-list-null-pointer
    - chore/scripts-function-documentation
```sh
# Take graph-implementation as an example
git checkout -b feat/graph-implementation
```

- Now, make any changes regarding this feature/area, only to its related branch
```sh
git add .
git commit -m "some commit message"
git push
```
- Once your changes are tested and finalized, go into the repository on github and into your branch
  - Here, you find a "contribute" button which will let you create a new pull request
- The pull request title should be in the format:
  - general-category(specific-category): description
  - in our example case, we can use something like the following:
    - feat(data-structure): graph implementation 
- Now, another member or yourself can approve or deny the pull request, as well as make any comments through the pull request menu.
- We can also delete the branch to keep things clean.


## Python Environment
### Initilization/Usage
1. Initialize a python virtual environment

```sh
python -m venv .venv
```

2. Enter the python environment


```sh
# macOS/Linux
source .venv/bin/activate

# Windows (Command Prompt)
.venv\Scripts\activate

# Windows (Powershell)
.venv\Scripts\Activate.ps1
```

3. Install Packages from requirements.txt

```sh
pip install -r requirements.txt
```
---
### Installing packages
1. Make sure you are in the virtual environment *(see [above](#initilizationusage))*
2. Install previously installed packages from requirements.txt *(also see [above](#initilizationusage))*
3. Install new package
```sh
pip install foo
```
4. Store any new packages in requirements.txt
```sh
pip freeze > requirements.txt
```
---

## Running Both Implementations

This repo contains two implementations of the same compiler backend:

- `Haskell Solution/` (Haskell pipeline, executed with `runghc`)
- `Imperative Solution/` (Python pipeline, executed with `python3`)

All commands below should be run from the repository root unless noted otherwise.

### 1) Haskell Solution

#### Run the compiler on one input file
```sh
runghc -i"Haskell Solution" "Haskell Solution/Main.hs" <num_registers> "Haskell Solution/<input_file>.txt"
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