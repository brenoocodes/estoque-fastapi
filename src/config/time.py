# import sys
# from pathlib import Path

# # Obtém o diretório do arquivo atual e seu diretório pai
# file = Path(__file__).resolve()
# parent = file.parent.parent.parent
# # Adiciona o diretório pai ao sys.path
# sys.path.append(str(parent))

# from src.models.models import Entradas
# from src.configure import get_db
from datetime import datetime, timedelta

def converter_horario(horario_utc3):
    # Subtrai 3 horas do horário UTC
    horario_local = horario_utc3 - timedelta(hours=3)
    
    # Formata a hora como 'HH:MM'
    hora_formatada = horario_local.strftime('%H:%M')
    
    # Formata o dia como 'YYYY-MM-DD'
    dia_formatado = horario_local.strftime('%d/%m/%Y')
    
    return {'hora': hora_formatada, 'dia' : dia_formatado}


# def buscar_entradas():
#     db = next(get_db())  # Obtém a sessão do banco de dados
#     entradas = db.query(Entradas).all()
#     lista_de_entradas = []
#     for entrada in entradas:
#         entrada_atual = {}
#         entrada_atual['horario'] = converter_horario(entrada.data_entrada)
        
#         lista_de_entradas.append(entrada_atual)
#     db.close()  # Fecha a sessão do banco de dados
#     return lista_de_entradas

# if __name__ == "__main__":
#     resultado = buscar_entradas()
#     print(resultado)
