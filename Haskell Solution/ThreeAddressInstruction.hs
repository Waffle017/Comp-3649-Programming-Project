module ThreeAddressInstruction 
(
    ThreeAddressInstruction(..),  -- the type
    
    TASequence,
    Operand(..),
      Opcode(..),
    makeInstruction,     -- function to make a single 3 address instruction
    displayTASequence,  
    liveDisplay,
    makeTASequence,
    convertSrc

)   
where

-- Data declaration
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


-- Function that makes a single 3 address instruction
-- purpose: assigns all inputed values into corresponding data
makeInstruction :: String -> Operand -> Opcode -> Operand -> ThreeAddressInstruction
makeInstruction dst src1 opcode src2 = ThreeAddressInstruction { dst = dst, src1 = src1, op = opcode, src2 = src2 }

-- Function that makes a TASequence
-- [String]: a list of live variables 
-- [ThreeAddressInstruction]: a list of TAI components
-- purpose: makes a pair of lists that holds the data for three address instructions and the list of live variables
makeTASequence :: [ThreeAddressInstruction] -> [String] -> TASequence
makeTASequence instr liveVars = (instr,liveVars)

-- Function that displays a 3 address instruction to the display
displayTASequence :: TASequence -> String
displayTASequence sequence = unlines (map singleTA (fst sequence))

-- Function that shows the set of live variables
liveDisplay :: TASequence -> String
liveDisplay live = unlines (snd live)

-- Helper function for displayTASequence
-- purpose: correctly formats a three address instruction as dst = src1 opcode src2
singleTA :: ThreeAddressInstruction -> String
singleTA instr = dst instr ++ " = " ++ convertSrc (src1 instr) ++ " " ++ convertOp (op instr) ++ " " ++ convertSrc (src2 instr)

-- Helper function that formats src properly 
-- purpose: converts src from the operand type to a string
convertSrc :: Operand -> String
convertSrc (Var x) = x        -- if either src is a string
convertSrc (Num y) = "#" ++ show(y)  -- if either src is a number

-- Helper function that formats opcode properly
-- purpose: converts all opcodes into their corresponding strings
convertOp :: Opcode -> String
convertOp Add = "+"
convertOp Sub = "-"
convertOp Mul = "*"
convertOp Div = "/"