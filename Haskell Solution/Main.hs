module Main where 

import AssemblyInstruction(displayASMSequence)
import Allocator(buildInterferenceGraph, colourGraph, Colouring)
import ThreeAddressInstruction(ThreeAddressInstruction(..),TASequence, Operand(..), Opcode(..), makeTASequence, displayTASequence, makeInstruction)
import Codegen(codeGen, convertTAI)
import Parser(parseProgram, ParseResult, ParsedInstruction(..), prInstructions, prLiveOnExit)
import qualified Parser
import qualified Data.Map.Strict as Map
import Data.Maybe (isNothing)
import System.IO
import System.Environment (getArgs)
import Scanner(scanner, Token)

-- Helper to check if any variable spilled
hasSpills :: Colouring -> Bool
hasSpills colouring = any isNothing (Map.elems colouring)

-- Convert Parser.Operand to ThreeAddressInstruction.Operand
convertOperand :: Parser.Operand -> Operand
convertOperand (Parser.OpVar v) = Var v
convertOperand (Parser.OpInt n) = Num n

-- Convert operator string to Opcode
convertOp :: String -> Opcode
convertOp "+" = Add
convertOp "-" = Sub
convertOp "*" = Mul
convertOp "/" = Div
convertOp _   = Add

-- Convert a single ParsedInstruction to ThreeAddressInstruction
convertInstr :: ParsedInstruction -> ThreeAddressInstruction
convertInstr instr = makeInstruction
    (pDest instr)
    (convertOperand (pSrc1 instr))
    (convertOp (pOp instr))
    (maybe (Num 0) convertOperand (pSrc2 instr))

-- Convert ParseResult to TASequence
convertParsed :: ParseResult -> TASequence
convertParsed result = makeTASequence (map convertInstr (prInstructions result)) (prLiveOnExit result)

main :: IO()
main = do
    args <- getArgs
    let [numRegsStr, filename] = args
    let numRegisters = read numRegsStr :: Int
    content <- readFile filename
    let taiSequence = case parseProgram content of
            Left err -> error err
            Right result -> convertParsed result
    let allocatorInstrs = map convertTAI (fst taiSequence)
    let graph = buildInterferenceGraph allocatorInstrs (snd taiSequence)
    let colouring = colourGraph graph (Just numRegisters)



    if hasSpills colouring
        then putStrLn "Error: Register allocation failed (spill occurred). Cannot generate assembly."
        else putStr $ displayASMSequence (codeGen taiSequence colouring)

    let asmString = displayASMSequence (codeGen taiSequence colouring)
    writeFile "output.txt" asmString