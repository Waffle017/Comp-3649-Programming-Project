module Main where 

import AssemblyInstruction(displayASMSequence)
import Allocator(buildInterferenceGraph, colourGraph, Colouring)
import ThreeAddressInstruction(TASequence, Operand(..), Opcode(..),makeInstruction, makeTASequence, displayTASequence)
import Codegen(codeGen, convertTAI)
import qualified Data.Map.Strict as Map
import Data.Maybe (isNothing)
import System.IO

-- Helper to check if any variable spilled
hasSpills :: Colouring -> Bool
hasSpills colouring = any isNothing (Map.elems colouring)

main :: IO()
main = do
    content <- readFile "programpara.txt"


    {-
    --Setup Data
    let numRegisters = 3 -- Hard-coded register limit
    let instr1 = makeInstruction "a" (Num 10) Add (Num 5)
    let instr2 = makeInstruction "b" (Var "a") Mul (Num 2)
    let (instructions, liveVars) = makeTASequence [instr1, instr2] ["b"] 

    --Convert and Color
    let allocatorInstrs = map convertTAI instructions
    let graph = buildInterferenceGraph allocatorInstrs liveVars
    let colouring = colourGraph graph (Just numRegisters)

    --Program Output
    putStrLn "=== Three Address Code ==="
    putStrLn $ displayTASequence (instructions, liveVars)

    putStrLn "=== Register Allocation ==="
    print colouring -- Or use a custom "to string" function

    putStrLn "=== Assembly Output ==="
    if hasSpills colouring
        then putStrLn "Error: Register allocation failed (spill occurred). Cannot generate assembly."
        else putStr $ displayASMSequence (codeGen (instructions, liveVars) colouring)

    -- Next step: Once stdout works, use writeFile "output.asm" ...

    let asmString = displayASMSequence (codeGen (instructions, liveVars) colouring)
    writeFile "output.txt" asmString
    -}