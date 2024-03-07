from fastapi import status, HTTPException
from src.configure import app, router, db_dependency
from src.models import models
from src.config.senhas import *
from src.schemas.produtos.index import Produtos, ProdutosPut
from src.config.login import logado


@router.get("/produtos", status_code=status.HTTP_200_OK)
async def buscar_produtos(db: db_dependency, user: logado):
    if user is None:
        raise HTTPException(status_code=401, detail='Você não está logado')
    try:
        produtos = db.query(models.Produtos).all()
        lista_de_produtos = []
        for produto in produtos:
            produto_atual = {}
            produto_atual['id'] = produto.id
            produto_atual['nome'] = produto.nome
            produto_atual['nome_estoque'] = produto.nome_estoque
            produto_atual['preco'] = produto.preco
            produto_atual['quantidade'] = produto.quantidade
            lista_de_fornecedores = []
            for fornecedor in produto.fornecedores:
                fornecedor_atual = {}
                fornecedor_atual['id'] = fornecedor.id
                fornecedor_atual['cnpj'] = fornecedor.cnpj
                fornecedor_atual['razao_social'] = fornecedor.razao_social
                fornecedor_atual['nome_fantasia'] = fornecedor.nome_fantasia
                lista_de_fornecedores.append(fornecedor_atual)
            if len(lista_de_fornecedores) == 0:
                produto_atual['fornecedores'] = 'Esse produto ainda não tem nenhum fornecedor cadastrado'
            else:
                lista_de_fornecedores = sorted(lista_de_fornecedores, key=lambda x: x['nome_fantasia'])
                produto_atual['fornecedores'] = lista_de_fornecedores
            lista_de_produtos.append(produto_atual)
        if len(lista_de_produtos) == 0:
            return {'message': 'Ainda não temos nenum produto cadastrado'}
        else:
            lista_de_produtos = sorted(lista_de_produtos, key=lambda x: x['nome_estoque'])
            return {'produtos': lista_de_produtos}
    except Exception as e:
        print(e)
        return HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Ocorreu um error: {e}")


@router.get("/produtos/{id}", status_code=status.HTTP_200_OK)
async def buscar_produtos_por_id(db: db_dependency, user: logado, id: int):
    if user is None:
        raise HTTPException(status_code=401, detail='Você não está logado')
    try:
        produto = db.query(models.Produtos).filter(models.Produtos.id == id).first()
        if not produto:
            return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Produto não existe")
        produto_atual = {}
        produto_atual['id'] = produto.id
        produto_atual['nome'] = produto.nome
        produto_atual['nome_estoque'] = produto.nome_estoque
        produto_atual['preco'] = produto.preco
        produto_atual['quantidade'] = produto.quantidade
        lista_de_fornecedores = []
        for fornecedor in produto.fornecedores:
            fornecedor_atual = {}
            fornecedor_atual['id'] = fornecedor.id
            fornecedor_atual['cnpj'] = fornecedor.cnpj
            fornecedor_atual['razao_social'] = fornecedor.razao_social
            fornecedor_atual['nome_fantasia'] = fornecedor.nome_fantasia
            lista_de_fornecedores.append(fornecedor_atual)

        if len(lista_de_fornecedores) == 0:
            produto_atual['fornecedores'] = 'Esse produto ainda não tem nenhum fornecedor cadastrado'
        else:
            lista_de_fornecedores = sorted(lista_de_fornecedores, key=lambda x: x['nome_fantasia'])
            produto_atual['fornecedores'] = lista_de_fornecedores

        return(produto_atual)
        
    except Exception as e:
        print(e)
        return HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Ocorreu um error: {e}")

         
@router.post("/produtos", status_code=status.HTTP_201_CREATED)
async def criar_produtos(produto: Produtos, db: db_dependency, user: logado):
    if not user.get('is_admin', False):
        raise HTTPException(status_code=403, detail='Você não tem permissão para acessar esta funcionalidade')
    try:
        produto_existente = db.query(models.Produtos).filter(models.Produtos.nome == produto.nome).first()
        if produto_existente:
            return HTTPException(status_code=status.HTTP_200_OK, detail="Funcionário já existe")
        novo_produto = models.Produtos(nome=produto.nome, nome_estoque=produto.nome_estoque, medida=produto.medida, preco=produto.preco, quantidade=produto.quantidade)
        db.add(novo_produto)
        db.commit()
        db.refresh(novo_produto)
        return {'message': 'Novo produto criado com sucesso', 'data': novo_produto}
    except Exception as e:
        print(e)
        return HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Ocorreu um error: {e}")


@router.put("/produtos/{id}", status_code=status.HTTP_200_OK)
async def alterar_produto(db: db_dependency, user: logado, produto: ProdutosPut, id: int):
    if not user.get('is_admin', False):
        raise HTTPException(status_code=403, detail='Você não tem permissão para acessar esta funcionalidade')
    try:
        produto_existente = db.query(models.Produtos).filter(models.Produtos.id == id).first()
        if not produto_existente:
            return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Produto não existe")
        if produto.nome is not None:
            produto_existente.nome = produto.nome
        if produto.nome_estoque is not None:
            produto_existente.nome_estoque = produto.nome_estoque
        if produto.medida is not None:
            produto_existente.medida = produto.medida
        if produto.preco is not None:
            produto_existente.preco = produto.preco
        if produto.quantidade is not None:
            produto_existente.quantidade = produto.quantidade
        db.commit()
        db.refresh(produto_existente)
        return {"message": "produto atualizado com sucesso", "produto": produto_existente} 

    except Exception as e:
        print(e)
        return HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Ocorreu um error: {e}")

    
app.include_router(router)