from pydantic import BaseModel, EmailStr
from typing import Optional

class Produtos(BaseModel):
    nome: str
    nome_estoque: str
    medida: str
    preco: float
    quantidade: int

class ProdutosPut(BaseModel):
    nome: Optional[str] = None
    nome_estoque: Optional[str] = None
    medida: Optional[str] = None
    preco: Optional[float] = None
    quantidade: Optional[int] = None