# from flask import Flask, request, jsonify
# import cv2 as cv
# import numpy as np
# import io
# from PIL import Image
# from flask_cors import CORS

# app = Flask(__name__)
# CORS(app, resources={r"/api/*": {"origins": "*"}})

# # Função para extrair o maior contorno
# def extrairMaiorCtn(img):
#     imgGray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
#     imgTh = cv.adaptiveThreshold(
#         imgGray, 255, cv.ADAPTIVE_THRESH_GAUSSIAN_C, cv.THRESH_BINARY_INV, 11, 12
#     )
#     kernel = np.ones((2, 2), np.uint8)
#     imgDil = cv.dilate(imgTh, kernel)
#     contours, _ = cv.findContours(imgDil, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_NONE)
#     if not contours:
#         raise ValueError("Nenhum contorno encontrado na imagem.")
#     maiorCtn = max(contours, key=cv.contourArea)
#     x, y, w, h = cv.boundingRect(maiorCtn)
#     bbox = [x, y, w, h]
#     recorte = img[y : y + h, x : x + w]
#     recorte = cv.resize(recorte, (400, 750))
#     return recorte, bbox

# # Função para processar a imagem e calcular a pontuação
# def process_image(image_data, respostas_corretas, pesos):
#     # Carregar a imagem a partir dos dados recebidos
#     image = Image.open(io.BytesIO(image_data))
#     image = np.array(image)
#     img = cv.cvtColor(image, cv.COLOR_RGB2BGR)
#     img = cv.resize(img, (600, 700))
#     imgContours = img.copy()

#     # Extrair o maior contorno
#     try:
#         gabarito, bbox = extrairMaiorCtn(img)
#     except ValueError as e:
#         return {"error": str(e)}

#     imgGray2 = cv.cvtColor(gabarito, cv.COLOR_BGR2GRAY)
#     imgGray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
#     imgBlur = cv.GaussianBlur(imgGray, (5, 5), 1)
#     imgCanny = cv.Canny(imgBlur, 10, 50)

#     ret, imgTh = cv.threshold(imgGray2, 70, 255, cv.THRESH_BINARY_INV)
#     contours, _ = cv.findContours(imgCanny, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_NONE)
#     cv.drawContours(imgContours, contours, -1, (0, 255, 0), 2)
#     cv.rectangle(
#         img,
#         (bbox[0], bbox[1]),
#         (bbox[0] + bbox[2], bbox[1] + bbox[3]),
#         (0, 255, 0),
#         3,
#     )

#     # Definir 'campos' e 'resp' para 12 questões
#     campos = [
#         # Questão 1
#         (50, 305, 12, 18), (65, 305, 12, 18), (80, 305, 12, 18), (95, 305, 12, 18),
#         # Questão 2
#         (50, 335, 12, 18), (65, 335, 12, 18), (80, 335, 12, 18), (95, 335, 12, 18),
#         # Questão 3
#         (50, 365, 12, 18), (65, 365, 12, 18), (80, 365, 12, 18), (95, 365, 12, 18),
#         # Questão 4
#         (50, 390, 12, 18), (65, 390, 12, 18), (80, 390, 12, 18), (95, 390, 12, 18),
#         # Questão 5
#         (50, 420, 12, 18), (65, 420, 12, 18), (80, 420, 12, 18), (95, 420, 12, 18),
#         # Questão 6
#         (170, 305, 12, 18), (185, 305, 12, 18), (200, 305, 12, 18), (215, 305, 12, 18),
#         # Questão 7
#         (170, 335, 12, 18), (185, 335, 12, 18), (200, 335, 12, 18), (215, 335, 12, 18),
#         # Questão 8
#         (170, 365, 12, 18), (185, 365, 12, 18), (200, 365, 12, 18), (215, 365, 12, 18),
#         # Questão 9
#         (170, 390, 12, 18), (185, 390, 12, 18), (200, 390, 12, 18), (215, 390, 12, 18),
#         # Questão 10
#         (170, 420, 12, 18), (185, 420, 12, 18), (200, 420, 12, 18), (215, 420, 12, 18),
#         # Questão 11
#         (290, 305, 12, 18), (305, 305, 12, 18), (318, 305, 12, 18), (330, 305, 12, 18),
#         # Questão 12
#         (290, 335, 12, 18), (305, 335, 12, 18), (318, 335, 12, 18), (330, 335, 12, 18),
#     ]

#     resp = []
#     num_questoes = len(respostas_corretas)
#     opcoes = ['A', 'B', 'C', 'D']
#     for q in range(1, num_questoes + 1):
#         for opcao in opcoes:
#             resp.append(f'{q}-{opcao}')

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

#     # Processar as respostas marcadas
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

#     # Remover questões marcadas mais de uma vez
#     for pergunta in questoes_marcadas_mais_de_uma_vez:
#         marcadas_por_pergunta.pop(pergunta, None)

#     # Criar um dicionário das respostas corretas e pesos
#     respostas_corretas_dict = {}
#     for rc in respostas_corretas:
#         partes = rc.split('-')
#         if len(partes) == 2:
#             pergunta = int(partes[0])
#             resposta_letra = partes[1]
#             respostas_corretas_dict[pergunta] = resposta_letra

#     # Converter pesos para inteiros
#     try:
#         pesos = [int(p) for p in pesos]
#     except ValueError:
#         return {"error": "Pesos devem ser números inteiros"}

#     if len(pesos) != num_questoes:
#         return {"error": "O número de pesos não corresponde ao número de questões"}

#     # Calcular acertos, erros e pontuação com pesos
#     somaNum = 0  # Soma ponderada dos acertos
#     somaDen = sum(pesos)  # Soma dos pesos

#     resultado_respostas = {}

#     for i in range(1, num_questoes + 1):
#         resposta_marcada = marcadas_por_pergunta.get(i)
#         resposta_correta = respostas_corretas_dict.get(i)
#         peso = pesos[i - 1]
#         if resposta_marcada:
#             if resposta_marcada == resposta_correta:
#                 somaNum += peso
#                 status = "Correto"
#             else:
#                 status = "Incorreto"
#         else:
#             resposta_marcada = None
#             status = "Não respondida"
#         resultado_respostas[f"Questão {i}"] = {
#             "resposta_marcada": resposta_marcada,
#             "resposta_correta": resposta_correta,
#             "peso": peso,
#             "status": status,
#         }

#     pontuacao = int((somaNum * 100) / somaDen) if somaDen != 0 else 0

#     acertos = somaNum
#     erros = somaDen - somaNum

#     return {
#         "pontuacao": pontuacao,
#         "acertos": acertos,
#         "erros": erros,
#         "resultados": resultado_respostas,
#     }

# @app.route('/api/app12/upload', methods=['POST'])
# def upload_file():
#     if 'file' not in request.files:
#         return jsonify({"error": "Arquivo não encontrado"}), 400

#     file = request.files['file']
#     respostas_corretas = request.form.get('respostas_corretas', '')
#     pesos = request.form.get('peso', '')

#     if not respostas_corretas:
#         return jsonify({"error": "Respostas corretas não fornecidas"}), 400

#     if not pesos:
#         return jsonify({"error": "Pesos não fornecidos"}), 400

#     respostas_corretas = respostas_corretas.split(',')
#     pesos = pesos.split(',')

#     if file.filename == '':
#         return jsonify({"error": "Nenhum arquivo selecionado"}), 400

#     try:
#         resultado = process_image(file.read(), respostas_corretas, pesos)
#         return jsonify(resultado)
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500

# if __name__ == '__main__':
#     app.run(port=5005)


from flask import Flask, request, jsonify
import cv2 as cv
import numpy as np
import io
from PIL import Image
from flask_cors import CORS

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

    # Se não encontrar nenhum contorno, retorne (None, None)
    if not contours:
        return None, None

    maiorCtn = max(contours, key=cv.contourArea)
    x, y, w, h = cv.boundingRect(maiorCtn)
    bbox = [x, y, w, h]
    recorte = img[y : y + h, x : x + w]
    recorte = cv.resize(recorte, (400, 750))

    return recorte, bbox

def process_image(image_data, respostas_corretas, pesos):
    # Carrega a imagem
    image = Image.open(io.BytesIO(image_data))
    image = np.array(image)
    if image.ndim == 2:
        img = cv.cvtColor(image, cv.COLOR_GRAY2BGR)
    else:
        img = cv.cvtColor(image, cv.COLOR_RGB2BGR)
    img = cv.resize(img, (600, 700))

    # Extrai o maior contorno (gabarito)
    gabarito, bbox = extrairMaiorCtn(img)

    # Caso não encontre contorno (foto avulsa), retorna pontuação 0
    if gabarito is None or bbox is None:
        return {
            "pontuacao": 0,
            "acertos": 0,
            "erros": 0,
            "resultados": {}
        }

    imgGray2 = cv.cvtColor(gabarito, cv.COLOR_BGR2GRAY)
    imgGray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    imgBlur = cv.GaussianBlur(imgGray, (5, 5), 1)
    imgCanny = cv.Canny(imgBlur, 10, 50)
    ret, imgTh = cv.threshold(imgGray2, 70, 255, cv.THRESH_BINARY_INV)
    contours, _ = cv.findContours(
        imgCanny, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_NONE
    )

    # Define campos e respostas
    campos = []

    campos.append((48,300,18,25))
    campos.append((70,300,18,25))
    campos.append((90,300,18,25))
    campos.append((112,300,18,25))
    campos.append((48,340,18,25))
    campos.append((70,340,18,25))
    campos.append((90,340,18,25))
    campos.append((112,340,18,25))
    campos.append((48,375,18,25))
    campos.append((70,375,18,25))
    campos.append((90,375,18,25))
    campos.append((112,375,18,25))
    campos.append((48,412,18,25))
    campos.append((70,412,18,25))
    campos.append((90,412,18,25))
    campos.append((112,412,18,25))
    campos.append((48,450,18,25))
    campos.append((70,450,18,25))
    campos.append((90,450,18,25))
    campos.append((112,450,18,25))
    campos.append((168,300,18,25))
    campos.append((190,300,18,25))
    campos.append((210,300,18,25))
    campos.append((232,300,18,25))
    campos.append((168,340,18,25))
    campos.append((190,340,18,25))
    campos.append((210,340,18,25))
    campos.append((232,340,18,25))
    campos.append((168,375,18,25))
    campos.append((190,375,18,25))
    campos.append((210,375,18,25))
    campos.append((232,375,18,25))
    campos.append((168,412,18,25))
    campos.append((190,412,18,25))
    campos.append((210,412,18,25))
    campos.append((232,412,18,25))
    campos.append((168,450,18,25))
    campos.append((190,450,18,25))
    campos.append((210,450,18,25))
    campos.append((232,450,18,25))
    campos.append((285,300,18,25))
    campos.append((308,300,18,25))
    campos.append((330,300,18,25))
    campos.append((350,300,18,25))
    campos.append((285,338,18,25))
    campos.append((308,338,18,25))
    campos.append((330,338,18,25))
    campos.append((350,338,18,25))


    resp=[]


    resp.append(('1-A'))
    resp.append(('1-B'))
    resp.append(('1-C'))
    resp.append(('1-D'))
    resp.append(('2-A'))
    resp.append(('2-B'))
    resp.append(('2-C'))
    resp.append(('2-D'))
    resp.append(('3-A'))
    resp.append(('3-B'))
    resp.append(('3-C'))
    resp.append(('3-D'))
    resp.append(('4-A'))
    resp.append(('4-B'))
    resp.append(('4-C'))
    resp.append(('4-D'))
    resp.append(('5-A'))
    resp.append(('5-B'))
    resp.append(('5-C'))
    resp.append(('5-D'))
    resp.append(('6-A'))
    resp.append(('6-B'))
    resp.append(('6-C'))
    resp.append(('6-D'))
    resp.append(('7-A'))
    resp.append(('7-B'))
    resp.append(('7-C'))
    resp.append(('7-D'))
    resp.append(('8-A'))
    resp.append(('8-B'))
    resp.append(('8-C'))
    resp.append(('8-D'))
    resp.append(('9-A'))
    resp.append(('9-B'))
    resp.append(('9-C'))
    resp.append(('9-D'))
    resp.append(('10-A'))
    resp.append(('10-B'))
    resp.append(('10-C'))
    resp.append(('10-D'))
    resp.append(('11-A'))
    resp.append(('11-B'))
    resp.append(('11-C'))
    resp.append(('11-D'))
    resp.append(('12-A'))
    resp.append(('12-B'))
    resp.append(('12-C'))
    resp.append(('12-D'))

    num_questoes = 12
    opcoes = ['A', 'B', 'C', 'D']

    # Verifica se tamanho de respostas_corretas corresponde ao número de questões
    if len(respostas_corretas) != num_questoes:
        return {"error": "O número de respostas corretas não corresponde ao número de questões"}

    # Converte pesos em inteiros
    try:
        pesos = [int(p) for p in pesos]
    except ValueError:
        return {"error": "Pesos devem ser números inteiros"}

    # Verifica se tamanho de pesos corresponde ao número de questões
    if len(pesos) != num_questoes:
        return {"error": "O número de pesos não corresponde ao número de questões"}

    # Identifica quais campos foram marcados
    imgTh_shape = imgTh.shape[:2]
    respostas_marcadas = []
    for id, vg in enumerate(campos):
        x = int(vg[0])
        y = int(vg[1])
        w = int(vg[2])
        h = int(vg[3])
        campo = imgTh[y : y + h, x : x + w]
        height, width = campo.shape[:2]
        tamanho = height * width
        brancas = cv.countNonZero(campo)
        percentual = round((brancas / tamanho) * 100, 2)

        if percentual >= 15:
            respostas_marcadas.append(resp[id])

    # Trata questões marcadas mais de uma vez
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

    # Remove questões marcadas mais de uma vez
    for pergunta in questoes_marcadas_mais_de_uma_vez:
        marcadas_por_pergunta.pop(pergunta, None)

    # Monta dicionário de respostas corretas
    respostas_corretas_dict = {}
    for idx, resposta_certa in enumerate(respostas_corretas):
        partes = resposta_certa.split('-')
        if len(partes) == 2:
            pergunta = int(partes[0])
            resposta_letra = partes[1]
            respostas_corretas_dict[pergunta] = resposta_letra

    # Monta dicionário de pesos
    peso_dict = {}
    for idx, p in enumerate(pesos):
        peso_dict[idx + 1] = p

    somaNum = 0
    somaDen = sum(pesos)
    resultado_respostas = {}

    # Calcula pontuação
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
    return result

@app.route('/api/app10/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "Arquivo não encontrado"}), 400

    file = request.files['file']
    respostas_corretas = request.form.get('respostas_corretas', '')
    pesos = request.form.get('peso', '')

    if file.filename == '':
        return jsonify({"error": "Nenhum arquivo selecionado"}), 400

    # Converte respostas_corretas para lista
    respostas_corretas = respostas_corretas.split(',')

    # Converte pesos para lista
    if pesos:
        pesos = pesos.split(',')
    else:
        # Se não houver pesos, define todos como '1'
        pesos = ['1'] * len(respostas_corretas)

    try:
        resultado = process_image(file.read(), respostas_corretas, pesos)
        return jsonify(resultado)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(port=5005)