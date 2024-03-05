from fastapi import status, HTTPException
from fastapi.responses import JSONResponse
from src.configure import app, router, db_dependency
from src.models.models import Produtos, Funcionarios, Saidas
from src.schemas.saidas_do_estoque.index import SaidaEstoque, SaidaEstoquePut
from src.config.login import logado

@router.get("/saida_ao_estoque", status_code=status.HTTP_200_OK)
async def buscar_saida_do_estoque(db: db_dependency, user: logado):
    if user is None:
        raise HTTPException(status_code=401, detail='Você não está logado')
    try:
        saidas = db.query(Saidas).all()
        lista_de_saidas = []
        for saida in saidas:
            saida_atual = {}
            saida_atual['id'] = saida.id
            saida_atual['produto'] = saida.produtos.nome_estoque
            saida_atual['quantidade'] = saida.quantidade
            saida_atual['funcionário_responsável'] = saida.funcionario_responsavel.nome
            saida_atual['funcionário_solicitante'] = saida.funcionario_solicitante.nome
            lista_de_saidas.append(saida_atual)
        if len(lista_de_saidas) == 0:
            return {'Mensagem': 'Nenhuma saída cadastrada'}
        else:
            return {'saidas': lista_de_saidas}
    except Exception as e:
        print(e)
        return HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Ocorreu um erro: {e}")

@router.get("/saida_ao_estoque/logado", status_code=status.HTTP_200_OK)
async def buscar_saida_do_estoque(db: db_dependency, user: logado):
    if user is None:
        raise HTTPException(status_code=401, detail='Você não está logado')
    try:
        user_matricula = user.get('id')
        saidas = db.query(Saidas).filter(Saidas.funcionario_responsavel_matricula == user_matricula).all()
        lista_de_saidas = []
        for saida in saidas:
            saida_atual = {}
            saida_atual['id'] = saida.id
            saida_atual['produto'] = saida.produtos.nome_estoque
            saida_atual['quantidade'] = saida.quantidade
            saida_atual['funcionário_responsável'] = saida.funcionario_responsavel.nome
            saida_atual['funcionário_solicitante'] = saida.funcionario_solicitante.nome
            lista_de_saidas.append(saida_atual)
        if len(lista_de_saidas) == 0:
            return {'Mensagem': 'Nenhuma saída cadastrada'}
        else:
            return {'saidas': lista_de_saidas}



    except Exception as e:
        print(e)
        return HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Ocorreu um erro: {e}")

@router.post('/saida_ao_estoque', status_code=status.HTTP_201_CREATED)
async def adicionar_saida_do_estoque(db: db_dependency, user: logado, saida: SaidaEstoque):
    if user is None:
        raise HTTPException(status_code=401, detail='Você não está logado')
    
    try:
        produto_id = saida.produto_id
        quantidade = saida.quantidade
        funcionario_responsavel_matricula = user.get('id')
        funcionario_solicitante_matricula = saida.funcionario_solicitante_matricula
        
        produto_existente = db.query(Produtos).filter(Produtos.id == produto_id).first()
        if not produto_existente:
            return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Produto não encontrado")
        
        # Verifica se a quantidade em estoque é suficiente
        if produto_existente.quantidade < quantidade:
            return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Quantidade insuficiente em estoque")
        
       
        funcionario_solicitante = db.query(Funcionarios).filter(Funcionarios.matricula == funcionario_solicitante_matricula).first()
        if not funcionario_solicitante:
            return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Funcionário solicitante não encontrado")
        
        # Cria a nova saída do estoque
        nova_saida_do_estoque = Saidas(
            produto_id=produto_existente.id,
            quantidade=quantidade,
            funcionario_responsavel_matricula=funcionario_responsavel_matricula,
            funcionario_solicitante_matricula=funcionario_solicitante_matricula
        )
        db.add(nova_saida_do_estoque)
        
        # Atualiza a quantidade em estoque do produto
        produto_existente.quantidade -= quantidade
        
        db.commit()
        db.refresh(nova_saida_do_estoque)
        
        return {"Nova saída cadastrada com sucesso": nova_saida_do_estoque}
    
    except Exception as e:
        print(e)
        return HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Ocorreu um erro: {e}")

@router.put("/saida_ao_estoque/{saida_id}", status_code=status.HTTP_200_OK)
async def alterar_saida_do_estoque(db: db_dependency, user: logado, saida: SaidaEstoquePut, saida_id: int):
    if user is None:
        raise HTTPException(status_code=401, detail='Você não está logado')
    try:
        saida_existente = db.query(Saidas).filter(Saidas.id == saida_id).first()
        if not saida_existente:
            return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Saída não existe")
        

        if saida.produto_id is not None and saida.quantidade is not None:
            print('Passei no produto id e quantidade')
            produto_novo = db.query(Produtos).filter(Produtos.id == saida.produto_id).first()
            if not produto_novo:
                return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Produto novo não encontrado")


            produto_antigo = db.query(Produtos).filter(Produtos.id == saida_existente.produto_id).first()

            quantidade = saida_existente.quantidade

            produto_antigo.quantidade += quantidade

            nova_quantidade = saida.quantidade

            if produto_novo.quantidade < quantidade:
                return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Quantidade insuficiente em estoque")

            produto_novo.quantidade -= nova_quantidade

            saida_existente.produto_id = produto_novo.id
            saida_existente.quantidade = nova_quantidade

        # Atualiza apenas se houver alterações nos campos
        if saida.produto_id is not None:
            produto_novo = db.query(Produtos).filter(Produtos.id == saida.produto_id).first()
            if not produto_novo:
                return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Produto novo não encontrado")
            
            # Incrementa a quantidade do novo produto e decrementa a quantidade do produto antigo
            produto_antigo = db.query(Produtos).filter(Produtos.id == saida_existente.produto_id).first()
            quantidade = saida_existente.quantidade
            produto_antigo.quantidade += quantidade
            produto_novo.quantidade -= quantidade
            saida_existente.produto_id = produto_novo.id
        
        if saida.quantidade is not None:
            # Atualiza a quantidade de saída e ajusta a quantidade de estoque do produto
            quantidade_anterior = saida_existente.quantidade
            quantidade_nova = saida.quantidade
            produto = db.query(Produtos).filter(Produtos.id == saida_existente.produto_id).first()
            produto_quantidade = produto.quantidade + quantidade_anterior
            produto.quantidade += quantidade_anterior  # Incrementa a quantidade anterior de volta ao estoque

            if produto_quantidade < quantidade_nova:
                return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Quantidade insuficiente em estoque")

            produto.quantidade -= quantidade_nova      # Decrementa a nova quantidade do estoque
            saida_existente.quantidade = quantidade_nova
        
        
        if saida.funcionario_solicitante_matricula is not None:
            funcionario_novo = db.query(Funcionarios).filter(Funcionarios.matricula == saida.funcionario_solicitante_matricula).first()
            if not funcionario_novo:
                return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Funcionário solicitante novo não encontrado")
            saida_existente.funcionario_solicitante_matricula = funcionario_novo.matricula
        
        db.commit()
        db.refresh(saida_existente)

        return {"Saída alterada com sucesso": saida_existente}
    
    except Exception as e:
        print(e)
        return HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Ocorreu um erro: {e}")


@router.delete("/saida_ao_estoque/{saida_id}", status_code=status.HTTP_200_OK)
async def excluir_saida_do_estoque(db: db_dependency, user: logado, saida_id: int):
    if user is None:
        raise HTTPException(status_code=401, detail='Você não está logado')
    try:
        saida_existente = db.query(Saidas).filter(Saidas.id == saida_id).first()
        if not saida_existente:
            return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Saída não existe")
        
        produto = db.query(Produtos).filter(Produtos.id == saida_existente.produto_id).first()
        quantidade = saida_existente.quantidade
        produto.quantidade += quantidade  # Incrementa a quantidade de volta ao estoque
        
        db.delete(saida_existente)
        db.commit()

        return {"Saída excluída com sucesso": saida_existente}
    
    except Exception as e:
        print(e)
        return HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Ocorreu um erro: {e}")

app.include_router(router)
