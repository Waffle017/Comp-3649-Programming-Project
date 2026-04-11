module Scanner 
(
    Token(..),
    scanner
)



where
    
import Data.Char (isDigit)

data Token = VarToken String | NumToken Int | LiveToken | OpToken String
    deriving (Eq, Show)

-- Function that takes the content of the file and converts each into a token
scanner :: String -> [Token]
scanner content = map wordToToken (filter (/= "=") (words content))

-- Helper function that takes a single string (eg. "a") and decides which token constructor to put it in
wordToToken :: String -> Token
wordToToken str | str `elem` ["+", "-", "*", "/"] = OpToken str
                | str == "live:" = LiveToken
                | all isDigit str = NumToken (read str :: Int) 
                | otherwise  = VarToken str
                