import sqlite3
from datetime import datetime
from loteria_caixa import MegaSena

database_name = "loteria.sqlite"

def criar_bd():
  con = sqlite3.connect(database_name)
  cur = con.cursor()
  cur.execute("""
    CREATE TABLE IF NOT EXISTS megasena(
      sorteio INTEGER, 
      data DATE, 
      dezena1 INTEGER, 
      dezena2 INTEGER,
      dezena3 INTEGER, 
      dezena4 INTEGER,
      dezena5 INTEGER,
      dezena6 INTEGER,
      PRIMARY KEY(sorteio))
  """)
  con.close()

def abrir_bd():
  return sqlite3.connect(database_name)  

def popular_bd_megasena():
  concurso_atual = MegaSena()
  numero_jogo_atual = concurso_atual.numero()
  
  con = abrir_bd()
  cur = con.cursor()

  concursos_inseridos = 0

  for numero in range(1, numero_jogo_atual + 1):
    try:
      res = cur.execute("SELECT sorteio FROM megasena where sorteio = :sorteio", {"sorteio": numero})
      
      if res.fetchone() is None:
        print(u"Inserindo o concurso número {numero} no banco de dados".format(numero = numero))

        concurso = MegaSena(numero)
        lista_dezenas = concurso.listaDezenas()  
        if len(lista_dezenas) > 0:
          dezena1 = concurso.listaDezenas()[0]
          dezena2 = concurso.listaDezenas()[1]
          dezena3 = concurso.listaDezenas()[2]
          dezena4 = concurso.listaDezenas()[3]
          dezena5 = concurso.listaDezenas()[4]
          dezena6 = concurso.listaDezenas()[5] 

        jogo = (
          concurso.numero(), 
          datetime.strptime(concurso.dataApuracao(), '%d/%m/%Y'),
          dezena1, 
          dezena2, 
          dezena3,
          dezena4, 
          dezena5,
          dezena6
        )

        cur.execute("INSERT INTO megasena VALUES(?, ?, ?, ?, ?, ?, ?, ?)", jogo)
        con.commit()
        concursos_inseridos += 1
      else:
        print(u"Concurso número {numero} já existe no banco de dados".format(numero = numero))
    except:
      pass

  con.close()
  print("Total de concursos inseridos: {total}".format(total = concursos_inseridos)) 

criar_bd()
popular_bd_megasena()


#concurso = MegaSena()
#print(type(concurso.listaDezenas()))
#print(concurso.numero())
#print(concurso.dataApuracao())
                            
