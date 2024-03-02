import uvicorn
from src.routes.funcionarios.index import *
from src.routes.produtos.index import *


if __name__ == "__main__":
    uvicorn.run("src.configure:app", port=5000, reload=True)