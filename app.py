import os
import json
from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy, session
from sqlalchemy.sql import text

basedir = os.path.abspath(os.path.dirname(__file__))
database_name = "loteria.sqlite"
versao_api = '/api/v1'

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)

    app.config['SQLALCHEMY_DATABASE_URI'] =\
            'sqlite:///' + os.path.join(basedir, database_name)
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    #db = SQLAlchemy(app)

    with app.app_context():
        db.init_app(app)
        db.create_all()

    return app

class Megasena(db.Model):
  __tablename__ = 'megasena'
  
  sorteio = db.Column(db.Integer, primary_key=True)
  data    = db.Column(db.DateTime(timezone=True), nullable=True)
  dezena1 = db.Column(db.Integer, nullable=True)
  dezena2 = db.Column(db.Integer, nullable=True)
  dezena3 = db.Column(db.Integer, nullable=True)
  dezena4 = db.Column(db.Integer, nullable=True)
  dezena5 = db.Column(db.Integer, nullable=True)
  dezena6 = db.Column(db.Integer, nullable=True)

  def __repr__(self):
    return f'<Megasena {self.sorteio}>'  
  
  def serialize(self):
    return {
       "sorteio": self.sorteio,
       "data"   : self.data.strftime('%d/%m/%Y'),
       "dezena1": self.dezena1,
       "dezena2": self.dezena2,
       "dezena3": self.dezena3,
       "dezena4": self.dezena4,
       "dezena5": self.dezena5,
       "dezena6": self.dezena6,
    }

app = create_app()
   
@app.route('/')
def check():
    return 'Flask is working'    

@app.route('{versao_api}/megasena/resultados'.format(versao_api=versao_api), methods=["GET"])
def resultados_megasena():
  try:
    retorno = []
    sorteio = request.args.get('sorteio')
    if sorteio is None:
      jogos = Megasena.query.order_by(text("sorteio desc")).all()

      for jogo in jogos:
       jogo_json = jogo.serialize()
       retorno.append(jogo_json)
    else: 
      jogo = Megasena.query.get(sorteio) 
      if jogo is None:
        raise Exception(u"Jogo não encontrado")
      jogo_json = jogo.serialize()
      retorno.append(jogo_json)  
    
    response = app.response_class(
      response=json.dumps(retorno),
      status=200,
      mimetype='application/json'
    )
    return response
  except Exception as e:
    print(e)
    response = app.response_class(
      response=json.dumps({'msgErro': str(e)}),
      status=400,
      mimetype='application/json'
    )
    return response
  
@app.route('{versao_api}/megasena/numeros-contados'.format(versao_api=versao_api), methods=["GET"])
def numeros_contados_megasena():
  try: 
    numeros = {}
    for n in range(1,61):
      numeros[n] = 0

    for numero_coluna in range(1,7):
      coluna = 'dezena{numero_coluna}'.format(numero_coluna=numero_coluna)

      for numero, valor in numeros.items():
        resultado = db.session.execute(text('select count({coluna}) from megasena where {coluna} = {numero}'.format(coluna=coluna, numero=numero))).scalar()
        numeros[numero] = valor + resultado
    
    retorno_ordenado = sorted(numeros.items(), key=lambda x:x[1], reverse=True)

    retorno = []
    for chave, valor in retorno_ordenado:
      retorno.append({chave : valor}) 

    response = app.response_class(
      response=json.dumps(retorno),
      status=200,
      mimetype='application/json'
    )
    return response 
  except Exception as e:
    print(e)
    response = app.response_class(
      response=json.dumps({'msgErro': str(e)}),
      status=400,
      mimetype='application/json'
    )
    return response 
    
if __name__ == '__main__':
  app.run(host='0.0.0.0', port=9999, debug=True)