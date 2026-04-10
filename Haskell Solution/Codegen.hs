module Codegen 
(
    codeGen,
    singleToList,
    convertTAI
)


where

import Allocator (Colouring, Instruction(..), colourGraph, buildInterferenceGraph)
import ThreeAddressInstruction (TASequence, ThreeAddressInstruction,dst, src1, src2, op, Opcode(..), convertSrc)
import AssemblyInstruction (ASMSequence, makeAssembly, Opcode(..))
import qualified Data.Map.Strict as Map
import qualified ThreeAddressInstruction as TAI
import qualified AssemblyInstruction as ASM


-- Function that takes a sequence of three address instructions and converts it to an assembly sequence
codeGen :: TASequence -> Colouring -> ASMSequence 
codeGen threeAdd colour = concatMap (\instr -> singleToList instr colour) (fst threeAdd)


-- Function that takes a single three address instruction and puts it in the assembly sequence
singleToList :: ThreeAddressInstruction -> Colouring -> ASMSequence
singleToList instr colour = case Map.lookup (dst instr) colour of 
    Just (Just r) ->
        let reg = "R" ++ show r
            movInstr = makeAssembly MOV (TAI.src1 instr) reg
            opInstr  = makeAssembly (convert (op instr)) (TAI.src2 instr) reg
        in [movInstr, opInstr]
    Just Nothing -> []
    Nothing -> []

-- Helper function that converts three address opcode to ASM opcodes
convert :: TAI.Opcode -> ASM.Opcode
convert Add = ADD
convert Sub = SUB
convert Mul = MUL
convert Div = DIV


convertTAI :: ThreeAddressInstruction -> Allocator.Instruction
convertTAI instr = Allocator.Instruction 
    { Allocator.dest = dst instr
    , Allocator.src1 = convertSrc (TAI.src1 instr)
    , Allocator.src2 = Just (convertSrc (TAI.src2 instr))
    }