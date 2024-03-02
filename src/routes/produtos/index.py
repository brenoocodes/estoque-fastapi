from fastapi import status, HTTPException
from fastapi.responses import JSONResponse
from src.configure import app, router, db_dependency
from src.models import models
from src.config.senhas import *
from src.schemas.funcionarios.index import Funcionarios, FuncionarioPut
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
                produto_atual['fornecedores'] = lista_de_fornecedores
            lista_de_produtos.append(produto_atual)
        if len(lista_de_produtos) == 0:
            return {'message': 'Ainda não temos nenum produto cadastrado'}
        else:
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
            produto_atual['fornecedores'] = lista_de_fornecedores

        return(produto_atual)
        
    except Exception as e:
        print(e)
        return HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Ocorreu um error: {e}")

# @router.get("/funcionarios/{matricula}", status_code=status.HTTP_200_OK)
# async def buscar_funcionario_por_id(db: db_dependency, user: logado, matricula: int):
#     if user is None:
#         raise HTTPException(status_code=401, detail='Você não está logado')
#     if not user.get('is_admin', False):
#         raise HTTPException(status_code=403, detail='Você não tem permissão para acessar esta funcionalidade')
#     try:
#         funcionario = db.query(models.Funcionarios).filter(models.Funcionarios.matricula == matricula).first()
#         if not funcionario:
#             return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Esse funcionário não existe")
#         funcionario_atual = {}
#         funcionario_atual['matricula'] = funcionario.matricula
#         funcionario_atual['nome'] = funcionario.nome
#         funcionario_atual['email'] = funcionario.email
#         funcionario_atual['admin'] = funcionario.administrador
        
#         return JSONResponse(funcionario_atual)

#     except Exception as e:
#         print(e)
#         return HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Ocorreu um error: {e}")
         
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



# @router.put("/funcionarios/{matricula}", status_code=status.HTTP_200_OK)
# async def modificar_funcionario(db: db_dependency, user: logado, funcionario: FuncionarioPut, matricula: int):
#     if user is None:
#         raise HTTPException(status_code=401, detail='Você não está logado')
#     if not user.get('is_admin', False):
#         raise HTTPException(status_code=403, detail='Você não tem permissão para acessar esta funcionalidade')
#     try:
#         funcionario_existente = db.query(models.Funcionarios).filter(models.Funcionarios.matricula == matricula).first()
#         if not funcionario_existente:
#             raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Funcionário não encontrado")
#         if funcionario.email != funcionario_existente.email:
#             email_existente = db.query(models.Funcionarios).filter(models.Funcionarios.email == funcionario.email).first()
#             if email_existente:
#                 return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="E-mail já cadastrado")
#         if funcionario.nome is not None:
#             funcionario_existente.nome = funcionario.nome
#         if funcionario.email is not None:
#             funcionario_existente.email = funcionario.email
#         if funcionario.senha is not None:
#             senha = gerar_senha_criptografada(funcionario.senha)
#             funcionario_existente.senha = senha
#         if funcionario.administrador is not None:
#             funcionario_existente.admin = funcionario.administrador
#         db.commit()
#         db.refresh(funcionario_existente)

#         funcionario_atualizado = {
#             "matricula": funcionario_existente.matricula,
#             "nome": funcionario_existente.nome,
#             "email": funcionario_existente.email,
#             "administrador": funcionario_existente.administrador
#         }
#         return {"message": "Funcionário atualizado com sucesso", "funcionario": funcionario_atualizado}
        
#     except Exception as e:
#         print(e)
#         return HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Ocorreu um error: {e}")
    
app.include_router(router)