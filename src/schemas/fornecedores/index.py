from pydantic import BaseModel, EmailStr
from typing import Optional

class Fornecedores(BaseModel):
    cnpj: str
    razao_social: str
    nome_fantasia: str
    email: EmailStr
    telefone: str

class FornecedoresPut(BaseModel):
    cnpj: Optional[str] = None
    razao_social: Optional[str] = None
    nome_fantasia: Optional[str] = None
    email: Optional[EmailStr] = None
    telefone: Optional[str] = None
    