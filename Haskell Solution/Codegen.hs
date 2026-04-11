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
import qualified Data.Set as Set
import Data.Char (isDigit)
import qualified ThreeAddressInstruction as TAI -- differentiating similarly named data
import qualified AssemblyInstruction as ASM -- differentiating similarly named data 


-- Function that takes a sequence of three address instructions and converts it to an assembly sequence
codeGen :: TASequence -> Colouring -> ASMSequence 
codeGen threeAdd colour =
    let (body, loadedAfterBody) = buildBody (fst threeAdd) Set.empty
        stores = storeLiveOnExit (snd threeAdd) loadedAfterBody
    in body ++ stores
  where
    buildBody [] loaded = ([], loaded)
    buildBody (instr:rest) loaded =
      let (asmForInstr, loadedAfterInstr) = singleToListWithLoaded instr colour loaded
          (asmRest, loadedAfterRest) = buildBody rest loadedAfterInstr
      in (asmForInstr ++ asmRest, loadedAfterRest)

    storeLiveOnExit [] _ = []
    storeLiveOnExit (v:vs) loaded
      | isRealVarName v =
          case Map.lookup v colour of
            Just (Just r) -> makeAssembly MOV (TAI.Var ("R" ++ show r)) v : storeLiveOnExit vs loaded
            _ -> storeLiveOnExit vs loaded
      | otherwise = storeLiveOnExit vs loaded


-- Function that takes a single three address instruction and puts it in the assembly sequence 
singleToList :: ThreeAddressInstruction -> Colouring -> ASMSequence
singleToList instr colour = fst (singleToListWithLoaded instr colour Set.empty)

singleToListWithLoaded :: ThreeAddressInstruction -> Colouring -> Set.Set String -> (ASMSequence, Set.Set String)
singleToListWithLoaded instr colour loaded =
  case formatDestRegister (dst instr) colour of
    Nothing -> ([], loaded)
    Just destReg ->
      let (preloads, loadedAfterPreloads) = loadSourcesIfNeeded [TAI.src1 instr, TAI.src2 instr] loaded
          src1Formatted = formatOperand (TAI.src1 instr) colour
          movToDest =
            if destReg /= src1Formatted
              then [makeAssembly MOV (TAI.Var src1Formatted) destReg]
              else []
          src2Formatted = formatOperand (TAI.src2 instr) colour
          opInstr = [makeAssembly (convert (op instr)) (TAI.Var src2Formatted) destReg]
          loadedAfterDest =
            if isRealVarName (dst instr)
              then Set.insert (dst instr) loadedAfterPreloads
              else loadedAfterPreloads
      in (preloads ++ movToDest ++ opInstr, loadedAfterDest)
  where
    loadSourcesIfNeeded [] currentLoaded = ([], currentLoaded)
    loadSourcesIfNeeded (source:rest) currentLoaded =
      case source of
        TAI.Var v
          | isRealVarName v && not (Set.member v currentLoaded) ->
              let srcReg = formatOperand source colour
                  loadInstr = makeAssembly MOV (TAI.Var v) srcReg
                  (tailInstrs, nextLoaded) = loadSourcesIfNeeded rest (Set.insert v currentLoaded)
              in (loadInstr : tailInstrs, nextLoaded)
        _ -> loadSourcesIfNeeded rest currentLoaded

formatDestRegister :: String -> Colouring -> Maybe String
formatDestRegister name colour =
  case Map.lookup name colour of
    Just (Just r) -> Just ("R" ++ show r)
    _ -> Nothing

formatOperand :: TAI.Operand -> Colouring -> String
formatOperand operand colour =
  case operand of
    TAI.Num n -> "#" ++ show n
    TAI.Var v ->
      case Map.lookup v colour of
        Just (Just r) -> "R" ++ show r
        _ -> v

isRealVarName :: String -> Bool
isRealVarName name = not (isTempName name)
  where
    isTempName ('t':rest) = not (null rest) && all isDigit rest
    isTempName _ = False

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