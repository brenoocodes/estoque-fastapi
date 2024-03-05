from fastapi import status, HTTPException
from fastapi.responses import JSONResponse
from src.configure import app, router, db_dependency
from src.models.models import Produtos, ProdutosFornecedores, Fornecedores, Funcionarios, Entradas
from src.schemas.entradas_ao_estoque.index import EntradaEstoque, EntradaEstoquePut
from src.config.login import logado

@router.get("/entrada_ao_estoque", status_code=status.HTTP_200_OK)
async def buscar_entrada_ao_estoque(db: db_dependency, user: logado):
    if user is None:
        raise HTTPException(status_code=401, detail='Você não está logado')
    try:
        entradas = db.query(Entradas).all()
        lista_de_entradas = []
        for entrada in entradas:
            entrada_atual = {}
            entrada_atual['id'] = entrada.id
            entrada_atual['nota'] = entrada.nota
            entrada_atual['produto'] = entrada.produto.nome_estoque
            entrada_atual['fornecedor'] = entrada.fornecedor.nome_fantasia
            entrada_atual['quantidade'] = entrada.quantidade
            entrada_atual['funcionário_responsável'] = entrada.funcionario.nome
            lista_de_entradas.append(entrada_atual)
        if len(lista_de_entradas) == 0:
            return {'Mensagem': 'Nenhuma entrada cadastrada'}
        else:
            return {'entradas': lista_de_entradas}
    except Exception as e:
        print(e)
        return HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Ocorreu um error: {e}")

@router.get("/entrada_ao_estoque/logado", status_code=status.HTTP_200_OK)
async def buscar_entrada_ao_estoque(db: db_dependency, user: logado):
    if user is None:
        raise HTTPException(status_code=401, detail='Você não está logado')
    try:
        user_matricula = user.get('id')
        entradas = db.query(Entradas).filter(Entradas.funcionario_responsavel_matricula == user_matricula).all()
        
        lista_de_entradas = []
        for entrada in entradas:
            entrada_atual = {}
            entrada_atual['id'] = entrada.id
            entrada_atual['nota'] = entrada.nota
            entrada_atual['produto'] = entrada.produto.nome_estoque
            entrada_atual['fornecedor'] = entrada.fornecedor.nome_fantasia
            entrada_atual['quantidade'] = entrada.quantidade
            entrada_atual['funcionário_responsável'] = entrada.funcionario.nome
            lista_de_entradas.append(entrada_atual)
        if len(lista_de_entradas) == 0:
            return {'Mensagem': 'Nenhuma entrada cadastrada'}
        else:
            return {'entradas': lista_de_entradas}
    except Exception as e:
        print(e)
        return HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Ocorreu um error: {e}")

    

@router.post('/entrada_ao_estoque', status_code=status.HTTP_201_CREATED)
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
        
        nova_entrada_ao_estoque = Entradas(
            nota=nota,
            produto_id=produto_existente.id,
            fornecedor_id=fornecedor_existente.id,
            quantidade=quantidade,
            funcionario_responsavel_matricula=funcionario_matricula
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
    

@router.put("/entrada_ao_estoque/{entrada_id}", status_code=status.HTTP_200_OK)
async def alterar_entrada_ao_estoque(db: db_dependency, user: logado, entrada: EntradaEstoquePut, entrada_id: int):
    if user is None:
        raise HTTPException(status_code=401, detail='Você não está logado')
    try:
        entrada_existente = db.query(Entradas).filter(Entradas.id == entrada_id).first()
        if not entrada_existente:
            return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Entrada não existe")
        
        if entrada.produto_id is not None and entrada.quantidade is not None:
            print('Passei no produto id e quantidade')
            produto_novo = db.query(Produtos).filter(Produtos.id == entrada.produto_id).first()
            if not produto_novo:
                return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Produto novo não encontrado")


            produto_antigo = db.query(Produtos).filter(Produtos.id == entrada_existente.produto_id).first()

            quantidade = entrada_existente.quantidade

            produto_antigo.quantidade -= quantidade

            nova_quantidade = entrada.quantidade

            produto_novo.quantidade += nova_quantidade

            entrada_existente.produto_id = produto_novo.id
            entrada_existente.quantidade = nova_quantidade

        
        elif entrada.produto_id is not None:
            print('Passei no produto id')
            produto_novo = db.query(Produtos).filter(Produtos.id == entrada.produto_id).first()
            if not produto_novo:
                return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Produto novo não encontrado")


            produto_antigo = db.query(Produtos).filter(Produtos.id == entrada_existente.produto_id).first()

            quantidade = entrada_existente.quantidade

            produto_antigo.quantidade -= quantidade

            produto_novo.quantidade += quantidade

            entrada_existente.produto_id = produto_novo.id


        elif entrada.quantidade is not None:
            print('Passei na quantidade')

            produto = db.query(Produtos).filter(Produtos.id == entrada_existente.produto_id).first()

            quantidade = entrada_existente.quantidade

            produto.quantidade -= quantidade
            
            nova_quantidade = entrada.quantidade

            produto.quantidade += nova_quantidade

            entrada_existente.quantidade = nova_quantidade




        if entrada.nota is not None:
            entrada_existente.nota = entrada.nota
        
        if entrada.fornecedor_id is not None:
            novo_fornecedor = db.query(Fornecedores).filter(Fornecedores.id == entrada.fornecedor_id).first()
            if not novo_fornecedor:
                return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Fornecedor novo não encontrado")


        db.commit()
        db.refresh(entrada_existente)

        return {"Entrada alterada com sucesso": entrada_existente}




    except Exception as e:
        print(e)
        return HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Ocorreu um error: {e}")

@router.delete("/entrada_ao_estoque/{entrada_id}", status_code=status.HTTP_200_OK)
async def excluir_entrada_ao_estoque(db: db_dependency, user: logado, entrada_id: int):
    if user is None:
        raise HTTPException(status_code=401, detail='Você não está logado')
    try:
        entrada_existente = db.query(Entradas).filter(Entradas.id == entrada_id).first()
        if not entrada_existente:
            return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Entrada não existe")
        
        produto = db.query(Produtos).filter(Produtos.id == entrada_existente.produto_id).first()
        quantidade = entrada_existente.quantidade
        produto.quantidade -= quantidade
        
        db.delete(entrada_existente)
        db.commit()

        return {"Entrada excluida com sucesso": entrada_existente}

    except Exception as e:
        print(e)
        return HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Ocorreu um error: {e}")


app.include_router(router)