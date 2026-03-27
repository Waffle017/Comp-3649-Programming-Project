module ThreeAddressInstruction 
{
    ThreeAddressInstruction,

    dst,
    src1,
    src2,
    op
}
where

data Operand = Var String | Num Int
data Opcate = Add | Mul | Sub | Div
dst :: String
src1 :: Operand
src2 :: Operand
op :: Opcode