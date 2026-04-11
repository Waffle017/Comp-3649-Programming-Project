module Codegen 
(
    codeGen,
    singleToList,
    convertTAI
)


where

import Allocator (Colouring, Instruction(..), colourGraph, buildInterferenceGraph)
import ThreeAddressInstruction (TASequence, ThreeAddressInstruction(..), Opcode(..), convertSrc)
import AssemblyInstruction (ASMSequence, makeAssembly, Opcode(..))
import qualified Data.Map.Strict as Map
import qualified ThreeAddressInstruction as TAI -- differentiating similarly named data
import qualified AssemblyInstruction as ASM -- differentiating similarly named data 


-- Function that takes a sequence of three address instructions and converts it to an assembly sequence
codeGen :: TASequence -> Colouring -> ASMSequence 
codeGen threeAdd colour = concatMap (\instr -> singleToList instr colour) (fst threeAdd)


-- Function that takes a single three address instruction and puts it in the assembly sequence 
singleToList :: ThreeAddressInstruction -> Colouring -> ASMSequence
singleToList instr colour = case Map.lookup (dst instr) colour of 
    Just (Just r) ->
        let reg = "R" ++ show r -- Register number
            movInstr = makeAssembly MOV (TAI.src1 instr) reg -- create the first assembly line
            opInstr  = makeAssembly (convert (op instr)) (TAI.src2 instr) reg -- create the second assembly line
        in [movInstr, opInstr] -- put both into the ASMSequence
    Just Nothing -> []
    Nothing -> []

-- Helper function that converts three address opcode to ASM opcodes
-- purpose: properly formats it to how assembly displays it
convert :: TAI.Opcode -> ASM.Opcode
convert Add = ADD
convert Sub = SUB
convert Mul = MUL
convert Div = DIV

-- Function that converts the Three Address Instruction data into Instruction data in Allocator.hs
-- purpose: the types in ThreeAddressInstruction are the same as the ones in Allocator
convertTAI :: ThreeAddressInstruction -> Allocator.Instruction
convertTAI instr = Allocator.Instruction 
    { Allocator.dest = dst instr
    , Allocator.src1 = convertSrc (TAI.src1 instr)
    , Allocator.src2 = Just (convertSrc (TAI.src2 instr))
    }