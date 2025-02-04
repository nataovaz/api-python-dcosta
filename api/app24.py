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
#     contours, _ = cv.findContours(
#         imgDil, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_NONE
#     )

#     if not contours:
#         raise ValueError("Nenhum contorno encontrado na imagem.")

#     maiorCtn = max(contours, key=cv.contourArea)
#     x, y, w, h = cv.boundingRect(maiorCtn)
#     bbox = [x, y, w, h]
#     recorte = img[y : y + h, x : x + w]
#     recorte = cv.resize(recorte, (400, 750))

#     return recorte, bbox

# def process_image(image_data, respostas_corretas, peso):
#     # Carregar a imagem a partir dos dados enviados
#     image = Image.open(io.BytesIO(image_data))
#     image = np.array(image)
#     if image.ndim == 2:
#         # Imagem em escala de cinza
#         img = cv.cvtColor(image, cv.COLOR_GRAY2BGR)
#     else:
#         img = cv.cvtColor(image, cv.COLOR_RGB2BGR)
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
#     contours, _ = cv.findContours(
#         imgCanny, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_NONE
#     )
#     cv.drawContours(imgContours, contours, -1, (0, 255, 0), 2)
#     cv.rectangle(
#         img,
#         (bbox[0], bbox[1]),
#         (bbox[0] + bbox[2], bbox[1] + bbox[3]),
#         (0, 255, 0),
#         3,
#     )

#     # Definir 'campos' e 'resp' conforme o seu c처digo
#     campos = []
#     campos.extend([
#         (50,250,12,18),(65,250,12,18),(80,250,12,18),(95,250,12,18),
#         (50,280,12,18),(65,280,12,18),(80,280,12,18),(95,280,12,18),
#         (50,305,12,18),(65,305,12,18),(80,305,12,18),(95,305,12,18),
#         (50,335,12,18),(65,335,12,18),(80,335,12,18),(95,335,12,18),
#         (50,365,12,18),(65,365,12,18),(80,365,12,18),(95,365,12,18),
#         (50,390,12,18),(65,390,12,18),(80,390,12,18),(95,390,12,18),
#         (50,420,12,18),(65,420,12,18),(80,420,12,18),(95,420,12,18),
#         (50,450,12,18),(65,450,12,18),(80,450,12,18),(95,450,12,18),
#         (50,478,12,18),(65,478,12,18),(80,478,12,18),(95,478,12,18),
#         (50,508,12,18),(65,508,12,18),(80,508,12,18),(95,508,12,18),
#         (170,250,12,18),(185,250,12,18),(200,250,12,18),(215,250,12,18),
#         (170,280,12,18),(185,280,12,18),(200,280,12,18),(215,280,12,18),
#         (170,305,12,18),(185,305,12,18),(200,305,12,18),(215,305,12,18),
#         (170,335,12,18),(185,335,12,18),(200,335,12,18),(215,335,12,18),
#         (170,365,12,18),(185,365,12,18),(200,365,12,18),(215,365,12,18),
#         (170,390,12,18),(185,390,12,18),(200,390,12,18),(215,390,12,18),
#         (170,420,12,18),(185,420,12,18),(200,420,12,18),(215,420,12,18),
#         (170,450,12,18),(185,450,12,18),(200,450,12,18),(215,450,12,18),
#         (170,478,12,18),(185,478,12,18),(200,478,12,18),(215,478,12,18),
#         (170,508,12,18),(185,508,12,18),(200,508,12,18),(215,508,12,18),
#         (290,250,12,18),(304,250,12,18),(318,250,12,18),(330,250,12,18),
#         (290,280,12,18),(304,280,12,18),(318,280,12,18),(330,280,12,18),
#         (290,305,12,18),(304,305,12,18),(318,305,12,18),(330,305,12,18),
#         (290,335,12,18),(304,335,12,18),(318,335,12,18),(330,335,12,18),
#     ])

#     resp = []
#     for i in range(1, 25):
#         resp.extend([
#             f'{i}-A', f'{i}-B', f'{i}-C', f'{i}-D'
#         ])

#     respostas = []
#     for id, vg in enumerate(campos):
#         x = int(vg[0])
#         y = int(vg[1])
#         w = int(vg[2])
#         h = int(vg[3])
#         # cv.rectangle(gabarito, (x, y), (x + w, y + h), (0, 0, 255), 2)
#         campo = imgTh[y : y + h, x : x + w]
#         height, width = campo.shape[:2]
#         tamanho = height * width
#         brancas = cv.countNonZero(campo)
#         percentual = round((brancas / tamanho) * 100, 2)

#         if percentual >= 15:
#             respostas.append(resp[id])

#     # Processar as respostas marcadas para lidar com duplicatas
#     marcadas_por_pergunta = {}
#     questoes_marcadas_mais_de_uma_vez = set()

#     for r in respostas:
#         partes = r.split('-')
#         if len(partes) == 2:
#             pergunta = int(partes[0])
#             resposta_letra = partes[1]

#             if pergunta in marcadas_por_pergunta:
#                 questoes_marcadas_mais_de_uma_vez.add(pergunta)
#             else:
#                 marcadas_por_pergunta[pergunta] = resposta_letra

#     # Remover quest천es marcadas mais de uma vez
#     for pergunta in questoes_marcadas_mais_de_uma_vez:
#         marcadas_por_pergunta.pop(pergunta, None)

#     # Preparar respostas corretas e pesos
#     respostas_corretas_dict = {}
#     for idx, resposta_certa in enumerate(respostas_corretas):
#         partes = resposta_certa.split('-')
#         if len(partes) == 2:
#             pergunta = int(partes[0])
#             resposta_letra = partes[1]
#             respostas_corretas_dict[pergunta] = resposta_letra

#     peso_dict = {}
#     for idx, p in enumerate(peso):
#         partes = respostas_corretas[idx].split('-')
#         if len(partes) == 2:
#             pergunta = int(partes[0])
#             peso_dict[pergunta] = int(p)

#     somaNum = 0
#     somaDen = 0
#     resultados = {}
#     total_corretas = 0
#     total_incorretas = 0
#     total_nao_respondidas = 0

#     for pergunta in sorted(respostas_corretas_dict.keys()):
#         resposta_correta = respostas_corretas_dict[pergunta]
#         peso_pergunta = peso_dict.get(pergunta, 1)
#         resposta_marcada = marcadas_por_pergunta.get(pergunta)

#         if resposta_marcada:
#             if resposta_marcada == resposta_correta:
#                 somaNum += peso_pergunta
#                 status = "Correto"
#                 total_corretas += 1
#             else:
#                 status = "Incorreto"
#                 total_incorretas += 1
#         else:
#             resposta_marcada = None
#             status = "N찾o respondida"
#             total_nao_respondidas += 1

#         somaDen = sum(peso_dict.values())
#         #somaDen = sum(pesos)

#         resultados[f"Quest찾o {pergunta}"] = {
#             "peso": peso_pergunta,
#             "resposta_correta": resposta_correta,
#             "resposta_marcada": resposta_marcada,
#             "status": status,
#         }

#     pontuacao = int((somaNum / somaDen) * 100) if somaDen != 0 else 0

#     result = {
#         "acertos": total_corretas,
#         "erros": total_incorretas,
#         "pontuacao": pontuacao,
#         "resultados": resultados,
#     }
#     return result

# @app.route('/api/app24/upload', methods=['POST'])
# def upload_file():
#     if 'file' not in request.files:
#         return jsonify({"error": "Nenhum arquivo enviado"}), 400

#     file = request.files['file']
#     respostas_corretas = request.form.get('respostas_corretas', '')
#     peso = request.form.get('peso', '')

#     if file.filename == '':
#         return jsonify({"error": "Nenhum arquivo selecionado"}), 400

#     # Converter respostas_corretas para lista
#     respostas_corretas = respostas_corretas.split(',')
#     # Converter peso para lista
#     if peso:
#         peso = peso.split(',')
#     else:
#         # Default para pesos de 1
#         peso = ['1'] * len(respostas_corretas)

#     try:
#         resultado = process_image(file.read(), respostas_corretas, peso)
#         return jsonify(resultado)
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500

# if __name__ == '__main__':
#     app.run(port=5002)

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
    recorte = img[y:y+h, x:x+w]
    # Redimensiona para 500x750 (pode ser ajustado conforme sua necessidade)
    recorte = cv.resize(recorte, (500, 750))
    return recorte, bbox

def process_image(image_data, respostas_corretas, pesos):
    # Carrega a imagem e converte para BGR se necessário
    image = Image.open(io.BytesIO(image_data))
    image = np.array(image)
    if image.ndim == 2:
        img = cv.cvtColor(image, cv.COLOR_GRAY2BGR)
    else:
        img = cv.cvtColor(image, cv.COLOR_RGB2BGR)
    img = cv.resize(img, (600, 700))
    
    # Extrai o gabarito (área com as marcações)
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
    
    # ========================================================================
    # DEFINIÇÃO DOS CAMPOS (coordenadas) para 24 questões (cada uma com 4 opções)
    campos = []
    # Campos da primeira coluna (exemplo)
    campos.append((65,248,18,25))
    campos.append((87,248,18,25))
    campos.append((108,248,18,25))
    campos.append((130,248,18,25))
    
    campos.append((65,285,18,25))
    campos.append((87,285,18,25))
    campos.append((108,285,18,25))
    campos.append((130,285,18,25))
    
    campos.append((65,322,18,25))
    campos.append((87,322,18,25))
    campos.append((108,322,18,25))
    campos.append((130,322,18,25))
    
    campos.append((65,360,18,25))
    campos.append((87,360,18,25))
    campos.append((108,360,18,25))
    campos.append((130,360,18,25))
    
    campos.append((65,393,18,25))
    campos.append((87,393,18,25))
    campos.append((108,393,18,25))
    campos.append((130,393,18,25))
    
    campos.append((65,430,18,25))
    campos.append((87,430,18,25))
    campos.append((108,430,18,25))
    campos.append((130,430,18,25))
    
    campos.append((65,463,18,25))
    campos.append((87,463,18,25))
    campos.append((108,463,18,25))
    campos.append((130,463,18,25))
    
    campos.append((65,498,18,25))
    campos.append((87,498,18,25))
    campos.append((108,498,18,25))
    campos.append((130,498,18,25))
    
    campos.append((65,535,18,25))
    campos.append((87,535,18,25))
    campos.append((108,535,18,25))
    campos.append((130,535,18,25))
    
    campos.append((65,570,18,25))
    campos.append((87,570,18,25))
    campos.append((108,570,18,25))
    campos.append((130,570,18,25))
    
    # Campos da segunda coluna
    campos.append((212,248,18,25))
    campos.append((235,248,18,25))
    campos.append((258,248,18,25))
    campos.append((282,248,18,25))
    
    campos.append((212,285,18,25))
    campos.append((235,285,18,25))
    campos.append((258,285,18,25))
    campos.append((282,285,18,25))
    
    campos.append((212,322,18,25))
    campos.append((235,322,18,25))
    campos.append((258,322,18,25))
    campos.append((282,322,18,25))
    
    campos.append((212,360,18,25))
    campos.append((235,360,18,25))
    campos.append((258,360,18,25))
    campos.append((282,360,18,25))
    
    campos.append((212,393,18,25))
    campos.append((235,393,18,25))
    campos.append((258,393,18,25))
    campos.append((282,393,18,25))
    
    campos.append((212,430,18,25))
    campos.append((235,430,18,25))
    campos.append((258,430,18,25))
    campos.append((282,430,18,25))
    
    campos.append((212,463,18,25))
    campos.append((235,463,18,25))
    campos.append((258,463,18,25))
    campos.append((282,463,18,25))
    
    campos.append((212,498,18,25))
    campos.append((235,498,18,25))
    campos.append((258,498,18,25))
    campos.append((282,498,18,25))
    
    campos.append((212,535,18,25))
    campos.append((235,535,18,25))
    campos.append((258,535,18,25))
    campos.append((282,535,18,25))
    
    campos.append((212,570,18,25))
    campos.append((235,570,18,25))
    campos.append((258,570,18,25))
    campos.append((282,570,18,25))
    
    # Campos da terceira coluna
    campos.append((358,248,18,25))
    campos.append((383,248,18,25))
    campos.append((405,248,18,25))
    campos.append((432,248,18,25))
    
    campos.append((358,285,18,25))
    campos.append((383,285,18,25))
    campos.append((405,285,18,25))
    campos.append((432,285,18,25))
    
    campos.append((358,322,18,25))
    campos.append((383,322,18,25))
    campos.append((405,322,18,25))
    campos.append((432,322,18,25))
    
    campos.append((358,360,18,25))
    campos.append((383,360,18,25))
    campos.append((405,360,18,25))
    campos.append((432,360,18,25))
    
    # Rótulos para cada campo (de "1-A" até "24-D")
    resp = []
    resp.append('1-A')
    resp.append('1-B')
    resp.append('1-C')
    resp.append('1-D')
    resp.append('2-A')
    resp.append('2-B')
    resp.append('2-C')
    resp.append('2-D')
    resp.append('3-A')
    resp.append('3-B')
    resp.append('3-C')
    resp.append('3-D')
    resp.append('4-A')
    resp.append('4-B')
    resp.append('4-C')
    resp.append('4-D')
    resp.append('5-A')
    resp.append('5-B')
    resp.append('5-C')
    resp.append('5-D')
    resp.append('6-A')
    resp.append('6-B')
    resp.append('6-C')
    resp.append('6-D')
    resp.append('7-A')
    resp.append('7-B')
    resp.append('7-C')
    resp.append('7-D')
    resp.append('8-A')
    resp.append('8-B')
    resp.append('8-C')
    resp.append('8-D')
    resp.append('9-A')
    resp.append('9-B')
    resp.append('9-C')
    resp.append('9-D')
    resp.append('10-A')
    resp.append('10-B')
    resp.append('10-C')
    resp.append('10-D')
    resp.append('11-A')
    resp.append('11-B')
    resp.append('11-C')
    resp.append('11-D')
    resp.append('12-A')
    resp.append('12-B')
    resp.append('12-C')
    resp.append('12-D')
    resp.append('13-A')
    resp.append('13-B')
    resp.append('13-C')
    resp.append('13-D')
    resp.append('14-A')
    resp.append('14-B')
    resp.append('14-C')
    resp.append('14-D')
    resp.append('15-A')
    resp.append('15-B')
    resp.append('15-C')
    resp.append('15-D')
    resp.append('16-A')
    resp.append('16-B')
    resp.append('16-C')
    resp.append('16-D')
    resp.append('17-A')
    resp.append('17-B')
    resp.append('17-C')
    resp.append('17-D')
    resp.append('18-A')
    resp.append('18-B')
    resp.append('18-C')
    resp.append('18-D')
    resp.append('19-A')
    resp.append('19-B')
    resp.append('19-C')
    resp.append('19-D')
    resp.append('20-A')
    resp.append('20-B')
    resp.append('20-C')
    resp.append('20-D')
    resp.append('21-A')
    resp.append('21-B')
    resp.append('21-C')
    resp.append('21-D')
    resp.append('22-A')
    resp.append('22-B')
    resp.append('22-C')
    resp.append('22-D')
    resp.append('23-A')
    resp.append('23-B')
    resp.append('23-C')
    resp.append('23-D')
    resp.append('24-A')
    resp.append('24-B')
    resp.append('24-C')
    resp.append('24-D')
    
    num_questoes = 24
    opcoes = ['A', 'B', 'C', 'D']
    
    if len(respostas_corretas) != num_questoes:
        return {"error": "O número de respostas corretas não corresponde ao número de questões"}
    
    try:
        pesos = [int(p) for p in pesos]
    except ValueError:
        return {"error": "Pesos devem ser números inteiros"}
    if len(pesos) != num_questoes:
        return {"error": "O número de pesos não corresponde ao número de questões"}
    
    # Verifica os campos marcados
    respostas_marcadas = []
    for id, vg in enumerate(campos):
        x, y, w, h = vg
        campo = imgTh[y:y+h, x:x+w]
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
    
    # Monta os dicionários de respostas corretas e pesos
    respostas_corretas_dict = {}
    for idx, resposta_certa in enumerate(respostas_corretas):
        partes = resposta_certa.split('-')
        if len(partes) == 2:
            pergunta = int(partes[0])
            resposta_letra = partes[1]
            respostas_corretas_dict[pergunta] = resposta_letra
            
    peso_dict = {}
    for idx, p in enumerate(pesos):
        peso_dict[idx + 1] = p
    
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
            "status": status
        }
    
    pontuacao = int((somaNum / somaDen) * 100) if somaDen != 0 else 0
    result = {
        "pontuacao": pontuacao,
        "acertos": somaNum,
        "erros": somaDen - somaNum,
        "resultados": resultado_respostas
    }
    
    # ==========================================================================
    # ANOTAÇÃO NA IMAGEM – DESENHAR CÍRCULOS INDICANDO OS RESULTADOS
    # ==========================================================================
    # Mapeia cada opção para um índice (A=0, B=1, C=2, D=3)
    option_mapping = {'A': 0, 'B': 1, 'C': 2, 'D': 3}
    for questao in range(1, num_questoes + 1):
        resposta_correta = respostas_corretas_dict.get(questao)
        # Se o aluno respondeu e a resposta está correta (sem marcação múltipla), usa verde; senão, usa vermelho
        if questao in marcadas_por_pergunta and (marcadas_por_pergunta[questao] == resposta_correta):
            letra = marcadas_por_pergunta[questao]
            cor = (0, 255, 0)  # verde
        else:
            letra = resposta_correta
            cor = (0, 0, 255)  # vermelho
        if letra in option_mapping:
            index = (questao - 1) * 4 + option_mapping[letra]
            if index < len(campos):
                (x, y, w, h) = campos[index]
                center = (int(x + w/2), int(y + h/2))
                cv.circle(gabarito, center, 10, cor, -1)
    
    # Codifica a imagem anotada para base64
    retval, buffer = cv.imencode('.jpg', gabarito)
    jpg_as_text = base64.b64encode(buffer).decode('utf-8')
    result["imagem_resultado"] = "data:image/jpeg;base64," + jpg_as_text
    
    return result

@app.route('/api/app24/upload', methods=['POST'])
def upload_file():
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
        resultado = process_image(file.read(), respostas_corretas, pesos)
        return jsonify(resultado)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(port=5002)