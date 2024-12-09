from flask import Flask, request, jsonify
import cv2 as cv
import numpy as np
import io
from PIL import Image
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

def extrairMaiorCtn(img):
    imgGray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    imgTh = cv.adaptiveThreshold(
        imgGray, 255, cv.ADAPTIVE_THRESH_GAUSSIAN_C, cv.THRESH_BINARY_INV, 11, 12
    )
    kernel = np.ones((2, 2), np.uint8)
    imgDil = cv.dilate(imgTh, kernel)
    contours, _ = cv.findContours(
        imgDil, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_NONE
    )

    if not contours:
        raise ValueError("Nenhum contorno encontrado na imagem.")

    maiorCtn = max(contours, key=cv.contourArea)
    x, y, w, h = cv.boundingRect(maiorCtn)
    bbox = [x, y, w, h]
    recorte = img[y : y + h, x : x + w]
    recorte = cv.resize(recorte, (400, 750))

    return recorte, bbox

def process_image(image_data, respostas_corretas, peso):
    # Carregar a imagem a partir dos dados enviados
    image = Image.open(io.BytesIO(image_data))
    image = np.array(image)
    if image.ndim == 2:
        # Imagem em escala de cinza
        img = cv.cvtColor(image, cv.COLOR_GRAY2BGR)
    else:
        img = cv.cvtColor(image, cv.COLOR_RGB2BGR)
    img = cv.resize(img, (600, 700))
    imgContours = img.copy()

    # Extrair o maior contorno
    try:
        gabarito, bbox = extrairMaiorCtn(img)
    except ValueError as e:
        return {"error": str(e)}

    imgGray2 = cv.cvtColor(gabarito, cv.COLOR_BGR2GRAY)
    imgGray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    imgBlur = cv.GaussianBlur(imgGray, (5, 5), 1)
    imgCanny = cv.Canny(imgBlur, 10, 50)
    ret, imgTh = cv.threshold(imgGray2, 70, 255, cv.THRESH_BINARY_INV)
    contours, _ = cv.findContours(
        imgCanny, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_NONE
    )
    cv.drawContours(imgContours, contours, -1, (0, 255, 0), 2)
    cv.rectangle(
        img,
        (bbox[0], bbox[1]),
        (bbox[0] + bbox[2], bbox[1] + bbox[3]),
        (0, 255, 0),
        3,
    )

    # Definir 'campos' e 'resp' conforme o seu código
    campos = []
    campos.extend([
        (50,250,12,18),(65,250,12,18),(80,250,12,18),(95,250,12,18),
        (50,280,12,18),(65,280,12,18),(80,280,12,18),(95,280,12,18),
        (50,305,12,18),(65,305,12,18),(80,305,12,18),(95,305,12,18),
        (50,335,12,18),(65,335,12,18),(80,335,12,18),(95,335,12,18),
        (50,365,12,18),(65,365,12,18),(80,365,12,18),(95,365,12,18),
        (50,390,12,18),(65,390,12,18),(80,390,12,18),(95,390,12,18),
        (50,420,12,18),(65,420,12,18),(80,420,12,18),(95,420,12,18),
        (50,450,12,18),(65,450,12,18),(80,450,12,18),(95,450,12,18),
        (50,478,12,18),(65,478,12,18),(80,478,12,18),(95,478,12,18),
        (50,508,12,18),(65,508,12,18),(80,508,12,18),(95,508,12,18),
        (170,250,12,18),(185,250,12,18),(200,250,12,18),(215,250,12,18),
        (170,280,12,18),(185,280,12,18),(200,280,12,18),(215,280,12,18),
        (170,305,12,18),(185,305,12,18),(200,305,12,18),(215,305,12,18),
        (170,335,12,18),(185,335,12,18),(200,335,12,18),(215,335,12,18),
        (170,365,12,18),(185,365,12,18),(200,365,12,18),(215,365,12,18),
        (170,390,12,18),(185,390,12,18),(200,390,12,18),(215,390,12,18),
        (170,420,12,18),(185,420,12,18),(200,420,12,18),(215,420,12,18),
        (170,450,12,18),(185,450,12,18),(200,450,12,18),(215,450,12,18),
        (170,478,12,18),(185,478,12,18),(200,478,12,18),(215,478,12,18),
        (170,508,12,18),(185,508,12,18),(200,508,12,18),(215,508,12,18),
        (290,250,12,18),(304,250,12,18),(318,250,12,18),(330,250,12,18),
        (290,280,12,18),(304,280,12,18),(318,280,12,18),(330,280,12,18),
        (290,305,12,18),(304,305,12,18),(318,305,12,18),(330,305,12,18),
        (290,335,12,18),(304,335,12,18),(318,335,12,18),(330,335,12,18),
    ])

    resp = []
    for i in range(1, 25):
        resp.extend([
            f'{i}-A', f'{i}-B', f'{i}-C', f'{i}-D'
        ])

    respostas = []
    for id, vg in enumerate(campos):
        x = int(vg[0])
        y = int(vg[1])
        w = int(vg[2])
        h = int(vg[3])
        # cv.rectangle(gabarito, (x, y), (x + w, y + h), (0, 0, 255), 2)
        campo = imgTh[y : y + h, x : x + w]
        height, width = campo.shape[:2]
        tamanho = height * width
        brancas = cv.countNonZero(campo)
        percentual = round((brancas / tamanho) * 100, 2)

        if percentual >= 15:
            respostas.append(resp[id])

    # Processar as respostas marcadas para lidar com duplicatas
    marcadas_por_pergunta = {}
    questoes_marcadas_mais_de_uma_vez = set()

    for r in respostas:
        partes = r.split('-')
        if len(partes) == 2:
            pergunta = int(partes[0])
            resposta_letra = partes[1]

            if pergunta in marcadas_por_pergunta:
                questoes_marcadas_mais_de_uma_vez.add(pergunta)
            else:
                marcadas_por_pergunta[pergunta] = resposta_letra

    # Remover questões marcadas mais de uma vez
    for pergunta in questoes_marcadas_mais_de_uma_vez:
        marcadas_por_pergunta.pop(pergunta, None)

    # Preparar respostas corretas e pesos
    respostas_corretas_dict = {}
    for idx, resposta_certa in enumerate(respostas_corretas):
        partes = resposta_certa.split('-')
        if len(partes) == 2:
            pergunta = int(partes[0])
            resposta_letra = partes[1]
            respostas_corretas_dict[pergunta] = resposta_letra

    peso_dict = {}
    for idx, p in enumerate(peso):
        partes = respostas_corretas[idx].split('-')
        if len(partes) == 2:
            pergunta = int(partes[0])
            peso_dict[pergunta] = int(p)

    somaNum = 0
    somaDen = 0
    resultados = {}
    total_corretas = 0
    total_incorretas = 0
    total_nao_respondidas = 0

    for pergunta in sorted(respostas_corretas_dict.keys()):
        resposta_correta = respostas_corretas_dict[pergunta]
        peso_pergunta = peso_dict.get(pergunta, 1)
        resposta_marcada = marcadas_por_pergunta.get(pergunta)

        if resposta_marcada:
            if resposta_marcada == resposta_correta:
                somaNum += peso_pergunta
                status = "Correto"
                total_corretas += 1
            else:
                status = "Incorreto"
                total_incorretas += 1
        else:
            resposta_marcada = None
            status = "Não respondida"
            total_nao_respondidas += 1

        somaDen += peso_pergunta
        resultados[f"Questão {pergunta}"] = {
            "peso": peso_pergunta,
            "resposta_correta": resposta_correta,
            "resposta_marcada": resposta_marcada,
            "status": status,
        }

    pontuacao = int((somaNum / somaDen) * 100) if somaDen != 0 else 0

    result = {
        "acertos": total_corretas,
        "erros": total_incorretas,
        "pontuacao": pontuacao,
        "resultados": resultados,
    }
    return result

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "Nenhum arquivo enviado"}), 400

    file = request.files['file']
    respostas_corretas = request.form.get('respostas_corretas', '')
    peso = request.form.get('peso', '')

    if file.filename == '':
        return jsonify({"error": "Nenhum arquivo selecionado"}), 400

    # Converter respostas_corretas para lista
    respostas_corretas = respostas_corretas.split(',')
    # Converter peso para lista
    if peso:
        peso = peso.split(',')
    else:
        # Default para pesos de 1
        peso = ['1'] * len(respostas_corretas)

    try:
        resultado = process_image(file.read(), respostas_corretas, peso)
        return jsonify(resultado)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5002)
