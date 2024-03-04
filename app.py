import uvicorn
from src.routes.funcionarios.index import *
from src.routes.produtos.index import *
from src.routes.fornecedores.index import *
from src.routes.adicionar_produto_ao_fornecedor.index import *
from src.routes.entradas_ao_estoque.index import *
from src.routes.saidas_ao_estoque.index import *


# if __name__ == "__main__":
#     uvicorn.run("src.configure:app", port=5000, reload=True)