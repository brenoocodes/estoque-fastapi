from fastapi import status, HTTPException
from fastapi.responses import JSONResponse
from src.configure import app, router, db_dependency
from src.models.models import Produtos, ProdutosFornecedores, Fornecedores, Funcionarios, EntradasEstoque
from src.schemas.entradas_ao_estoque.index import EntradaEstoque, EntradaEstoquePut
from src.config.login import logado


@router.post('/adicionar_entrada_ao_estoque', status_code=status.HTTP_201_CREATED)
async def adicionar_entrada_ao_estoque(db: db_dependency, user: logado, entrada: EntradaEstoque):
    if user is None:
        raise HTTPException(status_code=401, detail='Você não está logado')
    
    try:
        nota = entrada.nota
        produto_id = entrada.produto_id
        fornecedor_id = entrada.fornecedor_id
        quantidade = entrada.quantidade
        funcionario_matricula = user.get('id')
        
        produto_existente = db.query(Produtos).filter(Produtos.id == produto_id).first()
        if not produto_existente:
            return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Produto não encontrado")
        
        fornecedor_existente = db.query(Fornecedores).filter(Fornecedores.id==fornecedor_id).first()
        if not fornecedor_existente:
            return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Fornecedor não encontrado")
        
        #colocar o if do relaciomento
        
        
        
        nova_entrada_ao_estoque = EntradasEstoque(
            nota=nota,
            produto_id=produto_existente.id,
            fornecedor_id=fornecedor_existente.id,
            quantidade=quantidade,
            funcionario_matricula=funcionario_matricula
        )
        db.add(nova_entrada_ao_estoque)
        #quantidade
        
        produto_existente.quantidade += quantidade
        db.commit()
        db.refresh(nova_entrada_ao_estoque)
        
        return {"Nova entrada cadastrada com sucesso": nova_entrada_ao_estoque}
        
    
    
    
    except Exception as e:
        print(e)
        return HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Ocorreu um error: {e}")

app.include_router(router)