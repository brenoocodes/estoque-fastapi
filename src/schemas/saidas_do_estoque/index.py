from pydantic import BaseModel, EmailStr
from typing import Optional

class SaidaEstoque(BaseModel):
    produto_id: int
    quantidade: int
    funcionario_solicitante_matricula: int

class SaidaEstoquePut(BaseModel):
    produto_id: Optional[int] = None
    quantidade: Optional[int] = None
    funcionario_solicitante_matricula: Optional[int] = None