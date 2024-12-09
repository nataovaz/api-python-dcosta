from flask import Flask, request, jsonify
import cv2 as cv
import numpy as np
import io
from PIL import Image
from flask_cors import CORS 

app = Flask(__name__)
CORS(app)

# Função para processar a imagem e calcular a nota
def process_image(image, respostas_corretas):
    def extrairMaiorCtn(img):
        imgGray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
        imgTh = cv.adaptiveThreshold(imgGray, 255, cv.ADAPTIVE_THRESH_GAUSSIAN_C, cv.THRESH_BINARY_INV, 11, 12)
        kernel = np.ones((2,2), np.uint8)
        imgDil = cv.dilate(imgTh, kernel)
        contours, _ = cv.findContours(imgDil, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_NONE)
        maiorCtn = max(contours, key=cv.contourArea)
        x, y, w, h = cv.boundingRect(maiorCtn)
        bbox = [x, y, w, h]
        recorte = img[y:y+h, x:x+w]
        recorte = cv.resize(recorte, (400, 750))
        return recorte, bbox

    campos = [
        (50,305,12,18), (65,305,12,18), (80,305,12,18), (95,305,12,18),
        (50,335,12,18), (65,335,12,18), (80,335,12,18), (95,335,12,18),
        (50,365,12,18), (65,365,12,18), (80,365,12,18), (95,365,12,18),
        (50,390,12,18), (65,390,12,18), (80,390,12,18), (95,390,12,18),
        (50,420,12,18), (65,420,12,18), (80,420,12,18), (95,420,12,18),
        (170,305,12,18), (185,305,12,18), (200,305,12,18), (215,305,12,18),
        (170,335,12,18), (185,335,12,18), (200,335,12,18), (215,335,12,18),
        (170,365,12,18), (185,365,12,18), (200,365,12,18), (215,365,12,18),
        (170,390,12,18), (185,390,12,18), (200,390,12,18), (215,390,12,18),
        (170,420,12,18), (185,420,12,18), (200,420,12,18), (215,420,12,18),
    ]

    # Converta respostas_corretas para um formato de resposta esperada
    respostas_corretas = respostas_corretas.split(',')

    # Carregar a imagem do upload
    image = Image.open(io.BytesIO(image))
    image = np.array(image)
    img = cv.cvtColor(image, cv.COLOR_RGB2BGR)
    img = cv.resize(img, (600, 700))
    imgContours = img.copy()
    gabarito, bbox = extrairMaiorCtn(img)
    imgGray2 = cv.cvtColor(gabarito, cv.COLOR_BGR2GRAY)
    imgGray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    imgBlur = cv.GaussianBlur(imgGray, (5, 5), 1)
    imgCanny = cv.Canny(imgBlur, 10, 50)

    ret, imgTh = cv.threshold(imgGray2, 70, 255, cv.THRESH_BINARY_INV)
    contours, _ = cv.findContours(imgCanny, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_NONE)
    cv.drawContours(imgContours, contours, -1, (0, 255, 0), 2)

    cv.rectangle(img, (bbox[0], bbox[1]), (bbox[0] + bbox[2], bbox[1] + bbox[3]), (0, 255, 0), 3)

    respostasEncontradas = []
    for id, vg in enumerate(campos):
        x = int(vg[0])
        y = int(vg[1])
        w = int(vg[2])
        h = int(vg[3])
        cv.rectangle(gabarito, (x, y), (x + w, y + h), (0, 0, 255), 2)
        cv.rectangle(imgTh, (x, y), (x + w, y + h), (255, 255, 255), 1)
        campo = imgTh[y:y + h, x:x + w]
        height, width = campo.shape[:2]
        tamanho = height * width
        brancas = cv.countNonZero(campo)
        percentual = round((brancas / tamanho) * 100, 2)
        if percentual >= 18:
            cv.rectangle(gabarito, (x, y), (x + w, y + h), (255, 0, 0), 2)
            respostasEncontradas.append(f'{id//4 + 1}-{chr(65 + id%4)}')  # Alternativa em formato correto

    erros = 0
    acertos = 0
    resultado_respostas = {}
    if len(respostasEncontradas) == len(respostas_corretas):
        for num, res in enumerate(respostasEncontradas):
            if res == respostas_corretas[num]:
                acertos += 1
                resultado_respostas[f'Questão {num + 1}'] = {'resposta': res, 'status': 'Correto'}
            else:
                erros += 1
                resultado_respostas[f'Questão {num + 1}'] = {'resposta': res, 'status': 'Incorreto'}

    pontuacao = int(acertos * 10)

    return {'pontuacao': pontuacao, 'resultados': resultado_respostas}

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']
    respostas_corretas = request.form.get('respostas_corretas', '')

    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    try:
        resultado = process_image(file.read(), respostas_corretas)
        return jsonify(resultado)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/')
def home():
    return "API is running. Use /upload to process images."



if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
