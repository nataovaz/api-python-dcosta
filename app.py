from flask import Flask, request, jsonify
from flask_cors import CORS

# Importação das funções específicas de cada API
from api.app10 import process_image as process_app10
from api.app12 import process_image as process_app12
from api.app24 import process_image as process_app24

app = Flask(__name__)
CORS(app)

# Rota de verificação da API
@app.route('/')
def home():
    return "API Python está rodando! Use as rotas: /api/app10/upload, /api/app12/upload, /api/app24/upload."

@app.route('/test', methods=['GET'])
def test_api():
    return "API Python está rodando! Use as rotas: /api/app10/upload, /api/app12/upload, /api/app24/upload."

# Rota para a API 10
@app.route('/api/app10/upload', methods=['POST'])
def upload_app10():
    if 'file' not in request.files:
        return jsonify({"error": "Arquivo não encontrado"}), 400

    file = request.files['file']
    respostas_corretas = request.form.get('respostas_corretas', '').split(',')
    pesos = request.form.get('peso', '').split(',') or ['1'] * len(respostas_corretas)

    try:
        resultado = process_app10(file.read(), respostas_corretas, pesos)
        return jsonify(resultado)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Rota para a API 12
@app.route('/api/app12/upload', methods=['POST'])
def upload_app12():
    if 'file' not in request.files:
        return jsonify({"error": "Arquivo não encontrado"}), 400

    file = request.files['file']
    respostas_corretas = request.form.get('respostas_corretas', '').split(',')
    pesos = request.form.get('peso', '').split(',') or ['1'] * len(respostas_corretas)

    try:
        resultado = process_app12(file.read(), respostas_corretas, pesos)
        return jsonify(resultado)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Rota para a API 24
@app.route('/api/app24/upload', methods=['POST'])
def upload_app24():
    if 'file' not in request.files:
        return jsonify({"error": "Arquivo não encontrado"}), 400

    file = request.files['file']
    respostas_corretas = request.form.get('respostas_corretas', '').split(',')
    pesos = request.form.get('peso', '').split(',') or ['1'] * len(respostas_corretas)

    try:
        resultado = process_app24(file.read(), respostas_corretas, pesos)
        return jsonify(resultado)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
