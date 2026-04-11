module Allocator
(
    Colouring,
    Instruction(..),
    buildInterferenceGraph,
    colourGraph

)
where

import qualified Data.List as List
import qualified Data.Map.Strict as Map
import qualified Data.Set as Set
import Data.Char (isAlpha, isAlphaNum)


-- Equivalent to the Python Instruction objects consumed by
-- build_interference_graph(instructions, live_on_exit).
data Instruction = Instruction
  { dest :: String
  , src1 :: String
  , src2 :: Maybe String
  } deriving (Show)

-- Python `conflicts_list`   -> Haskell `Graph`
-- Python `colouring` dict   -> Haskell `Colouring`
type Graph = Map.Map String (Set.Set String)
type Colouring = Map.Map String (Maybe Int)

-- Mirrors InterferenceGraph.add_node(var).
addNode :: String -> Graph -> Graph
addNode var graph = Map.insertWith (\_ old -> old) var Set.empty graph

-- Mirrors InterferenceGraph.add_edge(var1, var2):
-- add undirected conflict edges (both directions), skip self-edges.
addEdge :: String -> String -> Graph -> Graph
addEdge v1 v2 graph
  | v1 == v2 = graph -- Same as Python early-return for self-edge.
  | otherwise =
      let g0 = addNode v1 (addNode v2 graph) -- Ensure both endpoints exist first.
          g1 = Map.adjust (Set.insert v2) v1 g0 -- Add v2 to v1 adjacency set.
      in Map.adjust (Set.insert v1) v2 g1 -- Add v1 to v2 adjacency set.

isVariableName :: String -> Bool
isVariableName [] = False
isVariableName (c:cs) =
  (isAlpha c || c == '_') && all (\x -> isAlphaNum x || x == '_') cs -- Match Python `type(x) is str` intent for symbolic vars.

splitOn :: Char -> String -> [String]
splitOn delim = go []
  where
    go acc [] = [reverse acc] -- Emit final token.
    go acc (x:xs)
      | x == delim = reverse acc : go [] xs -- Delimiter ends current token.
      | otherwise = go (x:acc) xs -- Keep collecting characters.

-- Python instructions are serialized in gen.py as:
--   dest \t src1 \t op \t src2
-- This parser rebuilds that shape for allocation.
parseInstruction :: String -> Maybe Instruction
parseInstruction line =
  case splitOn '\t' line of
    [d, s1, _, s2raw] ->
      let s2 = if s2raw == "-" then Nothing else Just s2raw -- "-" is our None sentinel from gen.py.
      in Just (Instruction d s1 s2) -- `op` field is unused for interference, so we ignore it.
    _ -> Nothing -- Skip malformed input rows.

buildInterferenceGraph :: [Instruction] -> [String] -> Graph
buildInterferenceGraph instructions liveOnExit =
  let initialLive = Set.fromList (filter isVariableName liveOnExit) -- Python: current_live = set(live_on_exit)
      initialGraph = foldr addNode Map.empty (Set.toList initialLive) -- Python: add each live var as node
  in go (reverse instructions) initialLive initialGraph -- Python: for instruction in reversed(instructions)
  where
    -- Direct translation of allocator.py backwards scan:
    -- for instruction in reversed(instructions):
    --   add edges from dest to every live var
    --   remove dest from live
    --   add src1/src2 to live when they are variable names
    go [] _ graph = graph
    go (instr:rest) currentLive graph =
      let d = dest instr -- Python: dest = instruction.dest
          graphWithEdges = foldl (\g liveVar -> addEdge d liveVar g) graph (Set.toList currentLive) -- Python: for live_var in current_live: add_edge(dest, live_var)
          liveAfterDef = Set.delete d currentLive -- Python: if dest in current_live: remove(dest)
          graphWithDest = addNode d graphWithEdges -- Python: graph.add_node(dest)
          (liveAfterSrc1, graphAfterSrc1) =
            if isVariableName (src1 instr)
              then (Set.insert (src1 instr) liveAfterDef, addNode (src1 instr) graphWithDest) -- Python: add src1 to live + node when src1 is variable
              else (liveAfterDef, graphWithDest) -- Python: ignore immediate src1 values
          (liveAfterSrc2, graphAfterSrc2) =
            case src2 instr of
              Just s2v | isVariableName s2v ->
                (Set.insert s2v liveAfterSrc1, addNode s2v graphAfterSrc1) -- Python: add src2 to live + node when src2 is variable
              _ ->
                (liveAfterSrc1, graphAfterSrc1) -- Python: skip missing/non-variable src2
          -- Keep parity with the Python pipeline's observed behaviour:
          -- variable src2 is treated as directly interfering with the destination,
          -- and binary variable operands are also marked as mutually interfering.
          graphAfterExtraEdges =
            let withDestSrc2 =
                  case src2 instr of
                    Just s2v | isVariableName s2v -> addEdge d s2v graphAfterSrc2
                    _ -> graphAfterSrc2
            in if isVariableName (src1 instr)
                 then case src2 instr of
                        Just s2v | isVariableName s2v -> addEdge (src1 instr) s2v withDestSrc2
                        _ -> withDestSrc2
                 else withDestSrc2
      in go rest liveAfterSrc2 graphAfterExtraEdges

chooseColour :: Set.Set Int -> Maybe Int -> Maybe Int
chooseColour used maybeLimit = go 0
  where
    go candidate
      | candidate `Set.member` used = go (candidate + 1) -- Python: while colour in used: colour += 1
      | otherwise =
          case maybeLimit of
            Just limit | candidate >= limit -> Nothing -- Python spill case: colour = None
            _ -> Just candidate -- Python: assign first available colour

-- Translation of InterferenceGraph.colour_graph(num_registers):
-- deterministic variable order, gather neighbour colours already assigned,
-- pick first available colour, mark as spill (Nothing) if beyond limit.
colourGraph :: Graph -> Maybe Int -> Colouring
colourGraph graph maybeLimit = foldl assign Map.empty orderedVars
  where
    orderedVars = List.sort (Map.keys graph) -- Python: deterministic sorted(self.conflicts_list)
    assign colouring var =
      let neighbours = Map.findWithDefault Set.empty var graph -- Neighbour list for this variable.
          used = Set.fromList
            [ colour
            | n <- Set.toList neighbours
            , Just maybeColour <- [Map.lookup n colouring] -- Only neighbours already coloured.
            , Just colour <- [maybeColour] -- Ignore spilled neighbours (Nothing).
            ]
          chosen = chooseColour used maybeLimit -- Greedy first-fit choice.
      in Map.insert var chosen colouring -- Store colour/spill for current var.

formatMapping :: Colouring -> [String]
formatMapping colouring =
  [ var ++ "\t" ++ maybe "spill" show reg
  | var <- List.sort (Map.keys colouring) -- Stable output order for easier testing.
  , let reg = Map.findWithDefault Nothing var colouring -- Convert Maybe Int -> "spill"/number.
  ]

-- Small CLI adapter used by gen.py:
-- stdin line 1: num registers
-- stdin line 2: live vars (space-separated)
-- stdin line 3+: serialized instructions
-- stdout: "var<TAB>reg" or "var<TAB>spill"
runAllocator :: IO ()
runAllocator = do
  content <- getContents -- Read full payload piped from gen.py.
  let ls = lines content -- Split into protocol lines.
  case ls of
    [] -> putStrLn "ERROR: missing input" -- Missing even register count.
    (numRegsLine:liveLine:instructionLines) ->
      let maybeLimit =
            case reads numRegsLine :: [(Int, String)] of
              [(n, "")] | n >= 0 -> Just n -- Valid register budget.
              _ -> Nothing -- Invalid budget falls back to unbounded colours.
          liveOnExit = if null liveLine then [] else words liveLine -- Space-separated final live set.
          instructions = [ i | Just i <- map parseInstruction instructionLines ] -- Parse valid rows only.
          graph = buildInterferenceGraph instructions liveOnExit -- Build interference graph.
          colouring = colourGraph graph maybeLimit -- Allocate register numbers / spills.
      in mapM_ putStrLn (formatMapping colouring) -- Emit mapping lines consumed by gen.py.
    _ -> putStrLn "ERROR: incomplete input" -- Not enough protocol lines.