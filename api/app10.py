# from flask import Flask, request, jsonify
# import cv2 as cv
# import numpy as np
# import io
# from PIL import Image
# from flask_cors import CORS

# app = Flask(__name__)
# CORS(app, resources={r"/api/*": {"origins": "*"}})

# def extrairMaiorCtn(img):
#     imgGray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
#     imgTh = cv.adaptiveThreshold(
#         imgGray, 255, cv.ADAPTIVE_THRESH_GAUSSIAN_C, cv.THRESH_BINARY_INV, 11, 12
#     )
#     kernel = np.ones((2, 2), np.uint8)
#     imgDil = cv.dilate(imgTh, kernel)
#     contours, _ = cv.findContours(imgDil, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_NONE)

#     # Se não encontrar nenhum contorno, retorne (None, None)
#     if not contours:
#         return None, None

#     maiorCtn = max(contours, key=cv.contourArea)
#     x, y, w, h = cv.boundingRect(maiorCtn)
#     bbox = [x, y, w, h]
#     recorte = img[y : y + h, x : x + w]
#     recorte = cv.resize(recorte, (400, 750))

#     return recorte, bbox

# def process_image(image_data, respostas_corretas, pesos):
#     # Carrega a imagem
#     image = Image.open(io.BytesIO(image_data))
#     image = np.array(image)
#     if image.ndim == 2:
#         img = cv.cvtColor(image, cv.COLOR_GRAY2BGR)
#     else:
#         img = cv.cvtColor(image, cv.COLOR_RGB2BGR)
#     img = cv.resize(img, (600, 700))

#     # Extrai o maior contorno (gabarito)
#     gabarito, bbox = extrairMaiorCtn(img)

#     # Caso não encontre contorno (foto avulsa), retorna pontuação 0
#     if gabarito is None or bbox is None:
#         return {
#             "pontuacao": 0,
#             "acertos": 0,
#             "erros": 0,
#             "resultados": {}
#         }

#     imgGray2 = cv.cvtColor(gabarito, cv.COLOR_BGR2GRAY)
#     imgGray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
#     imgBlur = cv.GaussianBlur(imgGray, (5, 5), 1)
#     imgCanny = cv.Canny(imgBlur, 10, 50)
#     ret, imgTh = cv.threshold(imgGray2, 70, 255, cv.THRESH_BINARY_INV)
#     contours, _ = cv.findContours(
#         imgCanny, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_NONE
#     )

#     # Define campos e respostas
#     campos = [
#           (48,300,18,25), (70,300,18,25), (90,300,18,25), (112,300,18,25),
#           (48,340,18,25), (70,340,18,25), (90,340,18,25), (112,340,18,25),
#           (48,375,18,25), (70,375,18,25), (90,375,18,25), (112,375,18,25),
#           (48,412,18,25), (70,412,18,25), (90,412,18,25), (112,412,18,25),
#           (48,450,18,25), (70,450,18,25), (90,450,18,25), (112,450,18,25),
#           (168,300,18,25), (190,300,18,25), (210,300,18,25), (232,300,18,25),
#           (168,340,18,25), (190,340,18,25), (210,340,18,25), (232,340,18,25),
#           (168,375,18,25), (190,375,18,25), (210,375,18,25), (232,375,18,25),
#           (168,412,18,25), (190,412,18,25), (210,412,18,25), (232,412,18,25),
#           (168,450,18,25), (190,450,18,25), (210,450,18,25), (232,450,18,25)
#      ]


#     resp = [
#         '1-A', '1-B', '1-C', '1-D',
#         '2-A', '2-B', '2-C', '2-D',
#         '3-A', '3-B', '3-C', '3-D',
#         '4-A', '4-B', '4-C', '4-D',
#         '5-A', '5-B', '5-C', '5-D',
#         '6-A', '6-B', '6-C', '6-D',
#         '7-A', '7-B', '7-C', '7-D',
#         '8-A', '8-B', '8-C', '8-D',
#         '9-A', '9-B', '9-C', '9-D',
#         '10-A', '10-B', '10-C', '10-D',
#     ]

#     num_questoes = 10
#     opcoes = ['A', 'B', 'C', 'D']

#     # Verifica se tamanho de respostas_corretas corresponde ao número de questões
#     if len(respostas_corretas) != num_questoes:
#         return {"error": "O número de respostas corretas não corresponde ao número de questões"}

#     # Converte pesos em inteiros
#     try:
#         pesos = [int(p) for p in pesos]
#     except ValueError:
#         return {"error": "Pesos devem ser números inteiros"}

#     # Verifica se tamanho de pesos corresponde ao número de questões
#     if len(pesos) != num_questoes:
#         return {"error": "O número de pesos não corresponde ao número de questões"}

#     # Identifica quais campos foram marcados
#     imgTh_shape = imgTh.shape[:2]
#     respostas_marcadas = []
#     for id, vg in enumerate(campos):
#         x = int(vg[0])
#         y = int(vg[1])
#         w = int(vg[2])
#         h = int(vg[3])
#         campo = imgTh[y : y + h, x : x + w]
#         height, width = campo.shape[:2]
#         tamanho = height * width
#         brancas = cv.countNonZero(campo)
#         percentual = round((brancas / tamanho) * 100, 2)

#         if percentual >= 15:
#             respostas_marcadas.append(resp[id])

#     # Trata questões marcadas mais de uma vez
#     marcadas_por_pergunta = {}
#     questoes_marcadas_mais_de_uma_vez = set()

#     for r in respostas_marcadas:
#         partes = r.split('-')
#         if len(partes) == 2:
#             pergunta = int(partes[0])
#             resposta_letra = partes[1]

#             if pergunta in marcadas_por_pergunta:
#                 questoes_marcadas_mais_de_uma_vez.add(pergunta)
#             else:
#                 marcadas_por_pergunta[pergunta] = resposta_letra

#     # Remove questões marcadas mais de uma vez
#     for pergunta in questoes_marcadas_mais_de_uma_vez:
#         marcadas_por_pergunta.pop(pergunta, None)

#     # Monta dicionário de respostas corretas
#     respostas_corretas_dict = {}
#     for idx, resposta_certa in enumerate(respostas_corretas):
#         partes = resposta_certa.split('-')
#         if len(partes) == 2:
#             pergunta = int(partes[0])
#             resposta_letra = partes[1]
#             respostas_corretas_dict[pergunta] = resposta_letra

#     # Monta dicionário de pesos
#     peso_dict = {}
#     for idx, p in enumerate(pesos):
#         peso_dict[idx + 1] = p

#     somaNum = 0
#     somaDen = sum(pesos)
#     resultado_respostas = {}

#     # Calcula pontuação
#     for pergunta in range(1, num_questoes + 1):
#         resposta_correta = respostas_corretas_dict.get(pergunta)
#         peso_pergunta = peso_dict.get(pergunta, 1)
#         resposta_marcada = marcadas_por_pergunta.get(pergunta)

#         if resposta_marcada:
#             if resposta_marcada == resposta_correta:
#                 somaNum += peso_pergunta
#                 status = "Correto"
#             else:
#                 status = "Incorreto"
#         else:
#             resposta_marcada = None
#             status = "Não respondida"

#         resultado_respostas[f"Questão {pergunta}"] = {
#             "resposta_marcada": resposta_marcada,
#             "resposta_correta": resposta_correta,
#             "peso": peso_pergunta,
#             "status": status,
#         }

#     pontuacao = int((somaNum / somaDen) * 100) if somaDen != 0 else 0

#     result = {
#         "pontuacao": pontuacao,
#         "acertos": somaNum,
#         "erros": somaDen - somaNum,
#         "resultados": resultado_respostas,
#     }
#     return result

# @app.route('/api/app10/upload', methods=['POST'])
# def upload_file():
#     if 'file' not in request.files:
#         return jsonify({"error": "Arquivo não encontrado"}), 400

#     file = request.files['file']
#     respostas_corretas = request.form.get('respostas_corretas', '')
#     pesos = request.form.get('peso', '')

#     if file.filename == '':
#         return jsonify({"error": "Nenhum arquivo selecionado"}), 400

#     # Converte respostas_corretas para lista
#     respostas_corretas = respostas_corretas.split(',')

#     # Converte pesos para lista
#     if pesos:
#         pesos = pesos.split(',')
#     else:
#         # Se não houver pesos, define todos como '1'
#         pesos = ['1'] * len(respostas_corretas)

#     try:
#         resultado = process_image(file.read(), respostas_corretas, pesos)
#         return jsonify(resultado)
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500

# if __name__ == '__main__':
#     app.run(port=5001)

from flask import Flask, request, jsonify
import cv2 as cv
import numpy as np
import io
from PIL import Image
from flask_cors import CORS
import base64

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

def extrairMaiorCtn(img):
    imgGray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    imgTh = cv.adaptiveThreshold(
        imgGray, 255, cv.ADAPTIVE_THRESH_GAUSSIAN_C, cv.THRESH_BINARY_INV, 11, 12
    )
    kernel = np.ones((2, 2), np.uint8)
    imgDil = cv.dilate(imgTh, kernel)
    contours, _ = cv.findContours(imgDil, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_NONE)

    if not contours:
        return None, None

    maiorCtn = max(contours, key=cv.contourArea)
    x, y, w, h = cv.boundingRect(maiorCtn)
    bbox = [x, y, w, h]
    recorte = img[y : y + h, x : x + w]
    recorte = cv.resize(recorte, (400, 750))
    return recorte, bbox

def process_image(image_data, respostas_corretas, pesos, num_questoes=10):
    # Carrega a imagem a partir dos bytes
    image = Image.open(io.BytesIO(image_data))
    image = np.array(image)
    if image.ndim == 2:
        img = cv.cvtColor(image, cv.COLOR_GRAY2BGR)
    else:
        img = cv.cvtColor(image, cv.COLOR_RGB2BGR)
    img = cv.resize(img, (600, 700))

    # Extrai o gabarito (maior contorno)
    gabarito, bbox = extrairMaiorCtn(img)
    if gabarito is None or bbox is None:
        return {
            "pontuacao": 0,
            "acertos": 0,
            "erros": 0,
            "resultados": {},
            "imagem_resultado": None
        }

    imgGray2 = cv.cvtColor(gabarito, cv.COLOR_BGR2GRAY)
    imgGray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    imgBlur = cv.GaussianBlur(imgGray, (5, 5), 1)
    imgCanny = cv.Canny(imgBlur, 10, 50)
    ret, imgTh = cv.threshold(imgGray2, 70, 255, cv.THRESH_BINARY_INV)
    contours, _ = cv.findContours(imgCanny, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_NONE)

    # Seleciona os campos e define os rótulos conforme o número de questões
    if num_questoes == 10:
        campos = [
            (48,300,18,25), (70,300,18,25), (90,300,18,25), (112,300,18,25),
            (48,340,18,25), (70,340,18,25), (90,340,18,25), (112,340,18,25),
            (48,375,18,25), (70,375,18,25), (90,375,18,25), (112,375,18,25),
            (48,412,18,25), (70,412,18,25), (90,412,18,25), (112,412,18,25),
            (48,450,18,25), (70,450,18,25), (90,450,18,25), (112,450,18,25),
            (168,300,18,25), (190,300,18,25), (210,300,18,25), (232,300,18,25),
            (168,340,18,25), (190,340,18,25), (210,340,18,25), (232,340,18,25),
            (168,375,18,25), (190,375,18,25), (210,375,18,25), (232,375,18,25),
            (168,412,18,25), (190,412,18,25), (210,412,18,25), (232,412,18,25),
            (168,450,18,25), (190,450,18,25), (210,450,18,25), (232,450,18,25)
        ]
        resp = [
            '1-A', '1-B', '1-C', '1-D',
            '2-A', '2-B', '2-C', '2-D',
            '3-A', '3-B', '3-C', '3-D',
            '4-A', '4-B', '4-C', '4-D',
            '5-A', '5-B', '5-C', '5-D',
            '6-A', '6-B', '6-C', '6-D',
            '7-A', '7-B', '7-C', '7-D',
            '8-A', '8-B', '8-C', '8-D',
            '9-A', '9-B', '9-C', '9-D',
            '10-A', '10-B', '10-C', '10-D',
        ]
    elif num_questoes == 12:
        campos = [
            (48,260,18,25), (70,260,18,25), (90,260,18,25), (112,260,18,25),
            (48,300,18,25), (70,300,18,25), (90,300,18,25), (112,300,18,25),
            (48,340,18,25), (70,340,18,25), (90,340,18,25), (112,340,18,25),
            (48,380,18,25), (70,380,18,25), (90,380,18,25), (112,380,18,25),
            (48,420,18,25), (70,420,18,25), (90,420,18,25), (112,420,18,25),
            (48,460,18,25), (70,460,18,25), (90,460,18,25), (112,460,18,25),

            (168,260,18,25), (190,260,18,25), (210,260,18,25), (232,260,18,25),
            (168,300,18,25), (190,300,18,25), (210,300,18,25), (232,300,18,25),
            (168,340,18,25), (190,340,18,25), (210,340,18,25), (232,340,18,25),
            (168,380,18,25), (190,380,18,25), (210,380,18,25), (232,380,18,25),
            (168,420,18,25), (190,420,18,25), (210,420,18,25), (232,420,18,25),
            (168,460,18,25), (190,460,18,25), (210,460,18,25), (232,460,18,25)
        ]
        resp = []
        for i in range(1, 13):
            for op in ['A', 'B', 'C', 'D']:
                resp.append(f"{i}-{op}")
    else:
        return {"error": "Número de questões não suportado"}

    if len(respostas_corretas) != num_questoes:
        return {"error": "O número de respostas corretas não corresponde ao número de questões"}
    try:
        pesos = [int(p) for p in pesos]
    except ValueError:
        return {"error": "Pesos devem ser números inteiros"}
    if len(pesos) != num_questoes:
        return {"error": "O número de pesos não corresponde ao número de questões"}

    # Identifica quais campos foram marcados
    respostas_marcadas = []
    for id, vg in enumerate(campos):
        x, y, w, h = vg
        campo = imgTh[y : y + h, x : x + w]
        height, width = campo.shape[:2]
        tamanho = height * width
        brancas = cv.countNonZero(campo)
        percentual = round((brancas / tamanho) * 100, 2)
        if percentual >= 15:
            respostas_marcadas.append(resp[id])

    # Trata marcações múltiplas por questão
    marcadas_por_pergunta = {}
    questoes_marcadas_mais_de_uma_vez = set()
    for r in respostas_marcadas:
        partes = r.split('-')
        if len(partes) == 2:
            pergunta = int(partes[0])
            resposta_letra = partes[1]
            if pergunta in marcadas_por_pergunta:
                questoes_marcadas_mais_de_uma_vez.add(pergunta)
            else:
                marcadas_por_pergunta[pergunta] = resposta_letra

    for pergunta in questoes_marcadas_mais_de_uma_vez:
        marcadas_por_pergunta.pop(pergunta, None)

    # Constrói dicionários com as respostas corretas e os pesos
    respostas_corretas_dict = {}
    for resposta_certa in respostas_corretas:
        partes = resposta_certa.split('-')
        if len(partes) == 2:
            pergunta = int(partes[0])
            resposta_letra = partes[1]
            respostas_corretas_dict[pergunta] = resposta_letra

    peso_dict = {idx + 1: p for idx, p in enumerate(pesos)}

    somaNum = 0
    somaDen = sum(pesos)
    resultado_respostas = {}

    for pergunta in range(1, num_questoes + 1):
        resposta_correta = respostas_corretas_dict.get(pergunta)
        peso_pergunta = peso_dict.get(pergunta, 1)
        resposta_marcada = marcadas_por_pergunta.get(pergunta)
        if resposta_marcada:
            if resposta_marcada == resposta_correta:
                somaNum += peso_pergunta
                status = "Correto"
            else:
                status = "Incorreto"
        else:
            resposta_marcada = None
            status = "Não respondida"

        resultado_respostas[f"Questão {pergunta}"] = {
            "resposta_marcada": resposta_marcada,
            "resposta_correta": resposta_correta,
            "peso": peso_pergunta,
            "status": status,
        }

    pontuacao = int((somaNum / somaDen) * 100) if somaDen != 0 else 0

    result = {
        "pontuacao": pontuacao,
        "acertos": somaNum,
        "erros": somaDen - somaNum,
        "resultados": resultado_respostas,
    }

    # ==========================================================================
    # ANOTAÇÃO NA IMAGEM – DESENHA OS MARCADORES
    # ==========================================================================
    option_mapping = {'A': 0, 'B': 1, 'C': 2, 'D': 3}
    for questao in range(1, num_questoes + 1):
        resposta_certa = respostas_corretas_dict.get(questao)
        if questao in marcadas_por_pergunta and (marcadas_por_pergunta[questao] == resposta_certa) and (questao not in questoes_marcadas_mais_de_uma_vez):
            letra = marcadas_por_pergunta[questao]
            color = (0, 255, 0)  # verde
        else:
            letra = resposta_certa
            color = (0, 0, 255)  # vermelho

        if letra in option_mapping:
            index = (questao - 1) * 4 + option_mapping[letra]
            if index < len(campos):
                (x, y, w, h) = campos[index]
                center = (int(x + w/2), int(y + h/2))
                cv.circle(gabarito, center, 10, color, -1)

    retval, buffer = cv.imencode('.jpg', gabarito)
    jpg_as_text = base64.b64encode(buffer).decode('utf-8')
    result["imagem_resultado"] = "data:image/jpeg;base64," + jpg_as_text

    return result

# Endpoint para 10 questões
@app.route('/api/app10/upload', methods=['POST'])
def upload_file_app10():
    if 'file' not in request.files:
        return jsonify({"error": "Arquivo não encontrado"}), 400
    file = request.files['file']
    respostas_corretas = request.form.get('respostas_corretas', '')
    pesos = request.form.get('peso', '')
    if file.filename == '':
        return jsonify({"error": "Nenhum arquivo selecionado"}), 400

    respostas_corretas = respostas_corretas.split(',')
    if pesos:
        pesos = pesos.split(',')
    else:
        pesos = ['1'] * len(respostas_corretas)

    try:
        resultado = process_image(file.read(), respostas_corretas, pesos, num_questoes=10)
        return jsonify(resultado)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Endpoint para 12 questões
@app.route('/api/app12/upload', methods=['POST'])
def upload_file_app12():
    if 'file' not in request.files:
        return jsonify({"error": "Arquivo não encontrado"}), 400
    file = request.files['file']
    respostas_corretas = request.form.get('respostas_corretas', '')
    pesos = request.form.get('peso', '')
    if file.filename == '':
        return jsonify({"error": "Nenhum arquivo selecionado"}), 400

    respostas_corretas = respostas_corretas.split(',')
    if pesos:
        pesos = pesos.split(',')
    else:
        pesos = ['1'] * len(respostas_corretas)

    try:
        resultado = process_image(file.read(), respostas_corretas, pesos, num_questoes=12)
        return jsonify(resultado)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(port=5001)