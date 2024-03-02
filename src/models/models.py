import sys
from pathlib import Path
# Obtém o diretório do arquivo atual e seu diretório pai
file = Path(__file__).resolve()
parent = file.parent.parent.parent
# Adiciona o diretório pai ao sys.path
sys.path.append(str(parent))

from sqlalchemy import Boolean, Column, Integer, Float, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship, backref
from src.configure import Base, engine
from datetime import datetime

class Funcionarios(Base):
    __tablename__ = 'funcionarios'
    # Atributos da tabela funcionarios
    matricula = Column(Integer, unique=True, nullable=False, primary_key=True)
    nome = Column(String(120), nullable=False)
    email = Column(String(50), unique=True, nullable=False)
    senha = Column(String(100), nullable=False)
    administrador = Column(Boolean, default=False)
    data_criacao = Column(DateTime, nullable=False, default=datetime.utcnow)

class Fornecedores(Base):
    __tablename__ = 'fornecedores'
    # Atributos da tabela fornecedores
    id = Column(Integer, primary_key=True)
    cnpj = Column(String(14), unique=True, nullable=False)
    razao_social = Column(String(255), nullable=False)
    nome_fantasia = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False)
    telefone = Column(String(14), nullable=False)

# Definição da classe Produtos
class Produtos(Base):
    __tablename__ = 'produtos'
    # Atributos da tabela produtos
    id = Column(Integer, primary_key=True)
    nome = Column(String(255), nullable=False, index=True)
    nome_estoque = Column(String(255), nullable=False)
    medida = Column(String(50), nullable=False)
    preco = Column(Float, default=0.0)
    quantidade = Column(Integer)

    # Relacionamento com a tabela Fornecedores
    fornecedores = relationship('Fornecedores', secondary='produtos_fornecedores', backref=backref('produtos', lazy='dynamic'))

# Definição da classe ProdutosFornecedores
class ProdutosFornecedores(Base):
    __tablename__ = 'produtos_fornecedores'
    # Atributos da tabela produtos_fornecedores
    produto_id = Column(Integer, ForeignKey('produtos.id'), primary_key=True)
    fornecedor_id = Column(Integer, ForeignKey('fornecedores.id'), primary_key=True)

# Definição da classe EntradasEstoque
class EntradasEstoque(Base):
    __tablename__ = 'entradaestoque'
    # Atributos da tabela entradaestoque
    id = Column(Integer, primary_key=True)
    nota = Column(String(50), nullable=False)
    produto_id = Column(Integer, ForeignKey('produtos.id'), nullable=False)
    fornecedor_id = Column(Integer, ForeignKey('fornecedores.id'), nullable=False)
    data_entrada = Column(DateTime, nullable=False, default=datetime.utcnow)
    quantidade = Column(Integer, nullable=False)
    funcionario_matricula = Column(Integer, ForeignKey('funcionarios.matricula'), nullable=False)

# Definição da classe SaidasEstoque
class SaidasEstoque(Base):
    __tablename__='saidasestoque'
    # Atributos da tabela saidasestoque
    id = Column(Integer, primary_key=True)
    produto_id = Column(Integer, ForeignKey('produtos.id'), nullable=False)
    data_saida = Column(DateTime, nullable=False, default=datetime.utcnow)
    quantidade = Column(Integer, nullable=False)
    funcionario_responsavel = Column(Integer, ForeignKey('funcionarios.matricula'), nullable=False)
    funcionario_requisitante = Column(Integer, ForeignKey('funcionarios.matricula'), nullable=False)

# Base.metadata.drop_all(bind=engine)
# Base.metadata.create_all(bind=engine)