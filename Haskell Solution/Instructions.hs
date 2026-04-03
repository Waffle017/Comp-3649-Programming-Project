module ThreeAddressInstruction 
(
    ThreeAddressInstruction,  -- the type
    
    makeInstruction,     -- function to make a single 3 address instruction
    TASequence,
    displayTASequence,
    liveDisplay,
    Operand(..),
    Opcode(..)
)   
where

data ThreeAddressInstruction = ThreeAddressInstruction
    {
        dst :: String
        ,src1 :: Operand
        ,src2 :: Operand
        ,op :: Opcode
    }
    deriving(Show)

data Operand = Var String | Num Int
    deriving (Show)
data Opcode = Add | Mul | Sub | Div
    deriving(Show)

type TASequence = ([ThreeAddressInstruction],[String])     -- a list of three-address instructions together with a list of variables.


__ Function that makes a single 3 address instruction
makeInstruction :: String -> Operand -> Opcode -> Operand -> ThreeAddressInstruction
makeInstruction dst src1 opcode src2 = ThreeAddressInstruction { dst = dst, src1 = src1, op = opcode, src2 = src2 }

-- Function that makes a TASequence
makeTASequence :: 

-- Function that displays a 3 address instruction to the display
displayTASequence :: TASequence -> String
displayTASequence sequence = unlines (map singleTA (fst sequence))

-- Function that shows the set of live variables
liveDisplay :: TASequence -> String
liveDisplay live = unlines (snd live)

-- Helper function for displayTASequence
singleTA :: ThreeAddressInstruction -> String
singleTA instr = dst instr ++ " = " ++ show (src1 instr) ++ show (op instr) ++ show (src2 instr)