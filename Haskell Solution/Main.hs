module Main where 

import AssemblyInstruction(displayASMSequence)
import Allocator(buildInterferenceGraph, colourGraph)
import ThreeAddressInstruction(TASequence, makeInstruction, makeTASequence, Operand(..), Opcode(..))
import Codegen(codeGen, convertTAI)
    
main :: IO()
main = do
    let numRegisters = 7
    let instr1 = makeInstruction "a" (Var "a") Add (Num 1) 
    let seq1 = makeTASequence [instr1]["t1"] 
    let temp = convertTAI instr1
    let graph = buildInterferenceGraph [temp]["t1"] 
    let colour = colourGraph graph (Just numRegisters)
    putStr(displayASMSequence (codeGen seq1 colour))