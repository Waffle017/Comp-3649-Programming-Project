{-# LANGUAGE ScopedTypeVariables #-}

-- parser.hs
-- This is a direct Haskell version of our Python parser.
-- It keeps the same behavior but prints a tab-delimited format that Python reads.

module Main where

import Control.Exception (IOException, try)
import Data.Char (isAlpha, isAlphaNum, isDigit, isSpace)
import Data.List (isPrefixOf)
import Data.Maybe (mapMaybe)
import qualified System.Environment as Env
import System.Exit (exitFailure)
import System.IO (hPutStrLn, stderr)

-- Tokens are intentionally simple so the parser stays easy to reason about.
data Token = TokVar String
           | TokInt Int
           | TokAssign
           | TokPlus
           | TokMinus
           | TokMul
           | TokDiv
           | TokLive
           deriving (Eq, Show)

data ParsedInstruction = ParsedInstruction
  { pDest :: String
  , pSrc1 :: Operand
  , pOp :: String
  , pSrc2 :: Maybe Operand
  }
  deriving (Eq, Show)

data Operand
  = OpVar String
  | OpInt Int
  deriving (Eq, Show)

data ParseResult = ParseResult
  { prInstructions :: [ParsedInstruction]
  , prLiveOnExit :: [String]
  , prVariables :: [String]
  }
  deriving (Eq, Show)

-- Turn one line of source text into tokens.
-- Unknown characters are ignored on purpose (for example ':' in "live:").
tokenizeLine :: String -> [Token]
tokenizeLine [] = []
tokenizeLine (c:cs)
  | isSpace c = tokenizeLine cs
  | isAlpha c =
      let (ident, rest) = span (\ch -> isAlphaNum ch || ch == '_') (c:cs)
       in (if ident == "live" then TokLive else TokVar ident) : tokenizeLine rest
  | isDigit c =
      let (digits, rest) = span isDigit (c:cs)
       in TokInt (read digits) : tokenizeLine rest
  | c == '=' = TokAssign : tokenizeLine cs
  | c == '+' = TokPlus : tokenizeLine cs
  | c == '-' = TokMinus : tokenizeLine cs
  | c == '*' = TokMul : tokenizeLine cs
  | c == '/' = TokDiv : tokenizeLine cs
  | otherwise = tokenizeLine cs

-- Parse one instruction line.
-- We follow the same simple "position count" idea as parser.py:
--   first variable -> destination
--   second value   -> src1
--   third value    -> src2
parseInstructionTokens :: [Token] -> Either String (ParsedInstruction, Maybe String)
parseInstructionTokens toks = go toks 1 Nothing Nothing Nothing Nothing Nothing
  where
    finish maybeDest maybeSrc1 maybeSrc2 maybeOp maybeFirstDest = -- End of line: build final instruction or fail.
      case (maybeDest, maybeSrc1, maybeOp) of
        (Just dst, Just src1, Just op) -> Right (ParsedInstruction dst src1 op maybeSrc2, maybeFirstDest)
        (Just dst, Just src1, Nothing) -> Right (ParsedInstruction dst src1 "=" maybeSrc2, maybeFirstDest) -- Allow simple assignment: a = 1
        _ -> Left "Invalid instruction format."

    go [] _ maybeDest maybeSrc1 maybeSrc2 maybeOp maybeFirstDest = -- No tokens left; finalize parse state.
      finish maybeDest maybeSrc1 maybeSrc2 maybeOp maybeFirstDest
    go (token:rest) count maybeDest maybeSrc1 maybeSrc2 maybeOp maybeFirstDest = -- Consume one token and recurse.
      case token of
        TokVar v
          | count == 1 -> -- Position 1: variable is destination.
              let nextCount = 2
                  nextDest = Just v
                  nextFirstDest = Just v -- Track the first destination for prVariables.
               in go rest nextCount nextDest maybeSrc1 maybeSrc2 maybeOp nextFirstDest
          | count == 2 -> -- Position 2: variable becomes src1.
              let nextCount = 3
                  nextSrc1 = Just (OpVar v)
               in go rest nextCount maybeDest nextSrc1 maybeSrc2 maybeOp maybeFirstDest
          | otherwise -> -- Position 3+: variable becomes/overwrites src2.
              let nextCount = count
                  nextSrc2 = Just (OpVar v)
               in go rest nextCount maybeDest maybeSrc1 nextSrc2 maybeOp maybeFirstDest
        TokInt n
          | count == 2 -> -- Position 2: integer becomes src1.
              let nextCount = 3
                  nextSrc1 = Just (OpInt n)
               in go rest nextCount maybeDest nextSrc1 maybeSrc2 maybeOp maybeFirstDest
          | otherwise -> -- Otherwise integer becomes/overwrites src2.
              let nextCount = count + 1
                  nextSrc2 = Just (OpInt n)
               in go rest nextCount maybeDest maybeSrc1 nextSrc2 maybeOp maybeFirstDest
        TokAssign -> -- '=' is syntax only; state does not change.
          let nextCount = count
           in go rest nextCount maybeDest maybeSrc1 maybeSrc2 maybeOp maybeFirstDest
        TokMinus -> -- Record '-' as the current operator.
          let nextOp = Just "-"
           in go rest count maybeDest maybeSrc1 maybeSrc2 nextOp maybeFirstDest
        TokPlus -> -- Record '+' as the current operator.
          let nextOp = Just "+"
           in go rest count maybeDest maybeSrc1 maybeSrc2 nextOp maybeFirstDest
        TokMul -> -- Record '*' as the current operator.
          let nextOp = Just "*"
           in go rest count maybeDest maybeSrc1 maybeSrc2 nextOp maybeFirstDest
        TokDiv -> -- Record '/' as the current operator.
          let nextOp = Just "/"
           in go rest count maybeDest maybeSrc1 maybeSrc2 nextOp maybeFirstDest
        TokLive -> Left "Unexpected 'live' token inside instruction." -- 'live' must only appear in the final live section.

-- Parse the whole program.
-- We read instructions until we hit "live:", then collect live vars from that line.
parseProgram :: String -> Either String ParseResult
parseProgram contents = walk (lines contents) [] [] []
  where
    walk [] _ _ _ =
      Left "Unexpected EOF: Missing 'live:' statement at the end of the file."
    walk (ln:rest) instructions vars liveVars
      | all isSpace ln = walk rest instructions vars liveVars
      | isLiveLine ln =
          let lineTokens = tokenizeLine ln
              liveCollected = collectLiveVars lineTokens
           in Right
                ParseResult
                  { prInstructions = reverse instructions
                  , prLiveOnExit = liveCollected
                  , prVariables = reverse vars
                  }
      | otherwise =
          case parseInstructionTokens (tokenizeLine ln) of
            Right (inst, mDest) ->
              let vars' = maybe vars (\d -> addUnique d vars) mDest
               in walk rest (inst : instructions) vars' liveVars
            Left err ->
              Left ("Parse error on line: " ++ ln ++ " (" ++ err ++ ")")

    isLiveLine ln =
      let trimmed = dropWhile isSpace ln
       in "live" `isPrefixOf` trimmed

    collectLiveVars = mapMaybe asVar . dropWhile (/= TokLive)
      where
        asVar (TokVar v) = Just v
        asVar _ = Nothing

    addUnique v seen =
      if v `elem` seen then seen else v : seen

-- Emit parse output in the text format that parser.py/gen.py expect.
-- Format:
--   INST <dest> <src1> <op> <src2-or-dash>
--   LIVE <var>
--   VAR  <var>
renderResult :: ParseResult -> String
renderResult result =
  unlines $
    map renderInst (prInstructions result)
      ++ map (\v -> "LIVE\t" ++ v) (prLiveOnExit result)
      ++ map (\v -> "VAR\t" ++ v) (prVariables result)
  where
    renderInst inst =
      "INST\t"
        ++ pDest inst
        ++ "\t"
        ++ renderOperand (pSrc1 inst)
        ++ "\t"
        ++ pOp inst
        ++ "\t"
        ++ maybe "-" renderOperand (pSrc2 inst)

    renderOperand (OpVar v) = v
    renderOperand (OpInt n) = show n

-- Small CLI entrypoint.
-- Usage: runghc parser.hs <filename>
main :: IO ()
main = do
  args <- Env.getArgs
  case args of
    [filename] -> do
      fileResult <- try (readFile filename) :: IO (Either IOException String)
      case fileResult of
        Left _ -> do
          hPutStrLn stderr "File not found"
          exitFailure
        Right contents ->
          case parseProgram contents of
            Left err -> do
              hPutStrLn stderr err
              exitFailure
            Right parsed ->
              putStr (renderResult parsed)
    _ -> do
      hPutStrLn stderr "Usage: runghc parser.hs <filename>"
      exitFailure
