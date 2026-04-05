
module AssemblyInstruction
(


    AssemblyInstruction,

    Opcode(..),
    Operand(..)


)
where

import ThreeAddressInstruction(Operand(..))

data AssemblyInstruction = AssemblyInstruction
    {
        dst :: String
        ,op :: Opcode
        ,src :: Operand
    }
    deriving(Show)

data Opcode = MOV | ADD | SUB | MUL | DIV
    deriving(Show)


-- Function that makes a single assembly instruction
makeAssembly :: Opcode -> Operand -> String -> AssemblyInstruction

