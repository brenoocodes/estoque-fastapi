from fastapi import status, HTTPException
from fastapi.responses import JSONResponse
from src.configure import app, router, db_dependency
from src.models.models import Produtos, ProdutosFornecedores, Fornecedores
from src.config.login import logado


@router.post("/adicionar_produto_ao_fornecedor/{fornecedor_id}/{produto_id}", status_code=status.HTTP_200_OK)
async def adicionar_produto_ao_fornecedor(db: db_dependency, user: logado, fornecedor_id: int, produto_id: int):
    if not user.get('is_admin', False):
        raise HTTPException(status_code=403, detail='Você não tem permissão para acessar esta funcionalidade')
    try:
        fornecedor_existente = db.query(Fornecedores).filter(Fornecedores.id == fornecedor_id).first()
        if not fornecedor_existente:
            return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Fornecedor não encontrado")
        
        produto_existente = db.query(Produtos).filter(Produtos.id == produto_id).first()
        if not produto_existente:
            return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Produto não encontrado")
        relacao = ProdutosFornecedores(
            fornecedor_id = fornecedor_existente.id,
            produto_id = produto_existente.id)
        db.add(relacao)
        db.commit()
        db.refresh(relacao)
        return {"message": f"A relação entre {fornecedor_existente.razao_social} e {produto_existente.nome} foi realizada com sucesso"}
        
    except Exception as e:
        print(e)
        return HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Ocorreu um error: {e}")



@router.delete("/excluir_produto_do_fornecedor/{fornecedor_id}/{produto_id}", status_code=status.HTTP_202_ACCEPTED)
async def excluir_produto_do_fornecedor(db: db_dependency, user: logado, fornecedor_id: int, produto_id: int):
    if not user.get('is_admin', False):
        raise HTTPException(status_code=403, detail='Você não tem permissão para acessar esta funcionalidade')
    try:
        # Correção da consulta
        relacao = db.query(ProdutosFornecedores).filter_by(produto_id=produto_id, fornecedor_id=fornecedor_id).first()
        if not relacao:
            return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Relação não encontrada")
        
        fornecedor_nome = db.query(Fornecedores).filter_by(id=fornecedor_id).first().nome_fantasia
        produto_nome = db.query(Produtos).filter_by(id=produto_id).first().nome
        db.delete(relacao)
        db.commit()
        # Mensagem corrigida
        return {"mensagem": f"A relação entre {fornecedor_nome} e {produto_nome} foi excluída com sucesso"}
        
    except Exception as e:
        print(e)
        return HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Ocorreu um erro: {e}")




app.include_router(router)