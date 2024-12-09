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

def process_image(image_data, respostas_corretas, pesos):
    # Load the image from the uploaded data
    image = Image.open(io.BytesIO(image_data))
    image = np.array(image)
    if image.ndim == 2:
        # Grayscale image
        img = cv.cvtColor(image, cv.COLOR_GRAY2BGR)
    else:
        img = cv.cvtColor(image, cv.COLOR_RGB2BGR)
    img = cv.resize(img, (600, 700))
    imgContours = img.copy()

    # Extract the largest contour
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

    # Define 'campos' and 'resp' as per your code
    campos = [
        (50, 305, 12, 18), (65, 305, 12, 18), (80, 305, 12, 18), (95, 305, 12, 18),
        (50, 335, 12, 18), (65, 335, 12, 18), (80, 335, 12, 18), (95, 335, 12, 18),
        (50, 365, 12, 18), (65, 365, 12, 18), (80, 365, 12, 18), (95, 365, 12, 18),
        (50, 390, 12, 18), (65, 390, 12, 18), (80, 390, 12, 18), (95, 390, 12, 18),
        (50, 420, 12, 18), (65, 420, 12, 18), (80, 420, 12, 18), (95, 420, 12, 18),
        (170, 305, 12, 18), (185, 305, 12, 18), (200, 305, 12, 18), (215, 305, 12, 18),
        (170, 335, 12, 18), (185, 335, 12, 18), (200, 335, 12, 18), (215, 335, 12, 18),
        (170, 365, 12, 18), (185, 365, 12,18), (200, 365, 12, 18), (215, 365, 12, 18),
        (170, 390, 12, 18), (185, 390, 12, 18), (200, 390, 12, 18), (215, 390, 12, 18),
        (170, 420, 12, 18), (185, 420, 12, 18), (200, 420, 12, 18), (215, 420, 12, 18),
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

    num_questoes = 10  # Number of questions
    opcoes = ['A', 'B', 'C', 'D']

    # Ensure the number of correct answers matches the number of questions
    if len(respostas_corretas) != num_questoes:
        return {"error": "O número de respostas corretas não corresponde ao número de questões"}

    # Ensure the number of weights matches the number of questions
    try:
        pesos = [int(p) for p in pesos]
    except ValueError:
        return {"error": "Pesos devem ser números inteiros"}

    if len(pesos) != num_questoes:
        return {"error": "O número de pesos não corresponde ao número de questões"}

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

    # Process the marked answers to handle duplicates
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

    # Remove questions marked more than once
    for pergunta in questoes_marcadas_mais_de_uma_vez:
        marcadas_por_pergunta.pop(pergunta, None)

    # Prepare correct answers and weights
    respostas_corretas_dict = {}
    for idx, resposta_certa in enumerate(respostas_corretas):
        partes = resposta_certa.split('-')
        if len(partes) == 2:
            pergunta = int(partes[0])
            resposta_letra = partes[1]
            respostas_corretas_dict[pergunta] = resposta_letra

    peso_dict = {}
    for idx, p in enumerate(pesos):
        peso_dict[idx + 1] = p  # Assuming the questions are numbered from 1

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
    return result

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "Arquivo não encontrado"}), 400

    file = request.files['file']
    respostas_corretas = request.form.get('respostas_corretas', '')
    pesos = request.form.get('peso', '')

    if file.filename == '':
        return jsonify({"error": "Nenhum arquivo selecionado"}), 400

    # Convert respostas_corretas to list
    respostas_corretas = respostas_corretas.split(',')

    # Convert pesos to list
    if pesos:
        pesos = pesos.split(',')
    else:
        # Default to weights of 1
        pesos = ['1'] * len(respostas_corretas)

    try:
        resultado = process_image(file.read(), respostas_corretas, pesos)
        return jsonify(resultado)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
