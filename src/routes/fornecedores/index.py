from fastapi import status, HTTPException
from src.configure import app, router, db_dependency
from src.models import models
from src.config.senhas import *
from src.schemas.fornecedores.index import Fornecedores, FornecedoresPut
from src.config.login import logado

@router.get("/fornecedores", status_code=status.HTTP_200_OK)
async def buscar_fornecedores(db: db_dependency, user: logado):
    if user is None:
        raise HTTPException(status_code=401, detail='Você não está logado')
    try:
        fornecedores = db.query(models.Fornecedores).all()
        lista_de_fornecedores = []
        for fornecedor in fornecedores:
            fornecedor_atual = {}
            fornecedor_atual['id'] = fornecedor.id
            fornecedor_atual['cnpj'] = fornecedor.cnpj
            fornecedor_atual['razao_social'] = fornecedor.razao_social
            fornecedor_atual['nome_fantasia'] = fornecedor.nome_fantasia
            fornecedor_atual['email'] = fornecedor.email
            fornecedor_atual['telefone'] = fornecedor.telefone
            lista_de_produtos = []
            for produto in fornecedor.produtos:
                produto_atual = {}
                produto_atual['id'] = produto.id
                produto_atual['nome'] = produto.nome
                produto_atual['nome_estoque'] = produto.nome_estoque
                lista_de_produtos.append(produto_atual)
            if len(lista_de_produtos) == 0:
                fornecedor_atual['produtos'] = 'Esse fornecedor ainda não tem produtos relacionados'
            else:
                lista_de_produtos = sorted(lista_de_produtos, key=lambda x: x['nome_estoque'])
                fornecedor_atual['produtos'] = lista_de_produtos
            lista_de_fornecedores.append(fornecedor_atual)
        if len(lista_de_fornecedores) == 0:
            return {'message': 'Ainda não temos nenhum fornecedor cadastrado'}
        else:
            lista_de_fornecedores = sorted(lista_de_fornecedores, key=lambda x: x['nome_fantasia'])
            return {'fornecedores': lista_de_fornecedores}
    except Exception as e:
        print(e)
        return HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Ocorreu um erro: {e}")


@router.get("/fornecedores/{id}", status_code=status.HTTP_200_OK)
async def buscar_fornecedor_por_id(db: db_dependency, user: logado, id: int):
    if user is None:
        raise HTTPException(status_code=401, detail='Você não está logado')
    try:
        fornecedor = db.query(models.Fornecedores).filter(models.Fornecedores.id == id).first()
        if not fornecedor:
            return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Fornecedor não existe")
        fornecedor_atual = {}
        fornecedor_atual['id'] = fornecedor.id
        fornecedor_atual['cnpj'] = fornecedor.cnpj
        fornecedor_atual['razao_social'] = fornecedor.razao_social
        fornecedor_atual['nome_fantasia'] = fornecedor.nome_fantasia
        fornecedor_atual['email'] = fornecedor.email
        fornecedor_atual['telefone'] = fornecedor.telefone
        lista_de_produtos = []
        for produto in fornecedor.produtos:
            produto_atual = {}
            produto_atual['id'] = produto.id
            produto_atual['nome'] = produto.nome
            produto_atual['nome_estoque'] = produto.nome_estoque
            lista_de_produtos.append(produto_atual)
        if len(lista_de_produtos) == 0:
            fornecedor_atual['produtos'] = 'Esse fornecedor ainda não tem produtos relacionados'
        else:
            fornecedor_atual['produtos'] = lista_de_produtos
        
        return fornecedor_atual

    except Exception as e:
        print(e)
        return HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Ocorreu um erro: {e}")


@router.post("/fornecedores", status_code=status.HTTP_201_CREATED)
async def criar_fornecedor(fornecedor: Fornecedores, db: db_dependency, user: logado):
    if not user.get('is_admin', False):
        raise HTTPException(status_code=403, detail='Você não tem permissão para acessar esta funcionalidade')
    try:
        fornecedor_existente = db.query(models.Fornecedores).filter(models.Fornecedores.cnpj == fornecedor.cnpj).first()
        if fornecedor_existente:
            return HTTPException(status_code=status.HTTP_200_OK, detail="Fornecedor já existe")
        novo_fornecedor = models.Fornecedores(cnpj=fornecedor.cnpj, razao_social=fornecedor.razao_social, nome_fantasia=fornecedor.nome_fantasia, email=fornecedor.email,
       telefone=fornecedor.telefone)
        
        db.add(novo_fornecedor)
        db.commit()
        db.refresh(novo_fornecedor)
        return {'message': 'Novo fornecedor criado com sucesso', 'data': novo_fornecedor}
    except Exception as e:
        print(e)
        return HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Ocorreu um erro: {e}")


@router.put("/fornecedores/{id}", status_code=status.HTTP_200_OK)
async def alterar_fornecedor(db: db_dependency, user: logado, fornecedor: FornecedoresPut, id: int):
    if not user.get('is_admin', False):
        raise HTTPException(status_code=403, detail='Você não tem permissão para acessar esta funcionalidade')
    try:
        fornecedor_existente = db.query(models.Fornecedores).filter(models.Fornecedores.id == id).first()
        if not fornecedor_existente:
            return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Fornecedor não existe")
        if fornecedor.cnpj is not None:
            fornecedor_existente.cnpj = fornecedor.cnpj
        if fornecedor.razao_social is not None:
            fornecedor_existente.razao_social = fornecedor.razao_social
        if fornecedor.nome_fantasia is not None:
            fornecedor_existente.nome_fantasia = fornecedor.nome_fantasia
        if fornecedor.email is not None:
            fornecedor_existente.email = fornecedor.email
        if fornecedor.telefone is not None:
            fornecedor_existente.telefone = fornecedor.telefone
        db.commit()
        db.refresh(fornecedor_existente)
        return {"message": "Fornecedor atualizado com sucesso", "fornecedor": fornecedor_existente}

    except Exception as e:
        print(e)
        return HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Ocorreu um erro: {e}")


app.include_router(router)


