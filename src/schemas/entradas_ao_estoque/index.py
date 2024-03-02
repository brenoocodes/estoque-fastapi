from pydantic import BaseModel, EmailStr
from typing import Optional

class EntradaEstoque(BaseModel):
    nota: str
    produto_id: int
    quantidade: int
    fornecedor_id: int

class EntradaEstoquePut(BaseModel):
    nota: Optional[str] = None
    produto_id: Optional[int] = None
    quantidade: Optional[int] = None
    fornecedor_id: Optional[int] = None
    