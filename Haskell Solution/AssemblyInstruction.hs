
module AssemblyInstruction
(


    AssemblyInstruction,

    Opcode(..),
    Operand(..),
    ASMSequence,
    makeAssembly,
    asmSequence,
    displayASMSequence


)
where

import ThreeAddressInstruction(Operand(..),convertSrc)

data AssemblyInstruction = AssemblyInstruction
    {
        dst :: String
        ,op :: Opcode
        ,src :: Operand
    }
    deriving(Show)

data Opcode = MOV | ADD | SUB | MUL | DIV
    deriving(Show)

type ASMSequence = [AssemblyInstruction]


-- Function that makes a single assembly instruction
-- purpose: assigns each input to its corresponding data 
makeAssembly :: Opcode -> Operand -> String -> AssemblyInstruction
makeAssembly op src dst = AssemblyInstruction { op = op, src = src, dst = dst}

-- Function that makes a list of assembly instructions
-- purpose: You have the list of all 
asmSequence :: [AssemblyInstruction] -> ASMSequence
asmSequence instr = instr

-- Helper function for displayASMSequence
singleASM :: AssemblyInstruction -> String
singleASM instr = show(op instr) ++ " " ++ convertSrc (src instr) ++ ", " ++ dst instr

displayASMSequence :: ASMSequence -> String
displayASMSequence sequence = unlines (map singleASM sequence)