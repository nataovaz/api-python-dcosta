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
        raise ValueError("Nenhum contorno encontrado na imagem.")

    maiorCtn = max(contours, key=cv.contourArea)
    x, y, w, h = cv.boundingRect(maiorCtn)
    bbox = [x, y, w, h]
    recorte = img[y:y+h, x:x+w]
    recorte = cv.resize(recorte, (400, 750))
    return recorte, bbox

def process_image(image_data, respostas_corretas, peso):
    # Carrega a imagem
    image = Image.open(io.BytesIO(image_data))
    image = np.array(image)
    if image.ndim == 2:
        img = cv.cvtColor(image, cv.COLOR_GRAY2BGR)
    else:
        img = cv.cvtColor(image, cv.COLOR_RGB2BGR)
    img = cv.resize(img, (600, 700))
    
    try:
        gabarito, bbox = extrairMaiorCtn(img)
    except Exception as e:
        return {"error": str(e)}
    
    imgGray2 = cv.cvtColor(gabarito, cv.COLOR_BGR2GRAY)
    imgGray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    imgBlur = cv.GaussianBlur(imgGray, (5, 5), 1)
    imgCanny = cv.Canny(imgBlur, 10, 50)
    ret, imgTh = cv.threshold(imgGray2, 70, 255, cv.THRESH_BINARY_INV)
    contours, _ = cv.findContours(imgCanny, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_NONE)

    # ========================================================================
    # DEFINIÇÃO DOS CAMPOS e RÓTULOS (para 24 questões – 4 opções cada)
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

    # Cria a lista de rótulos: "1-A" até "24-D"
    resp = []
    for i in range(1, 25):
        resp.extend([f'{i}-A', f'{i}-B', f'{i}-C', f'{i}-D'])

    # ========================================================================
    # DETECÇÃO DAS MARCAÇÕES
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

    # Trata duplicidade: para cada pergunta, se houver mais de uma marcação, descarta
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

    # Prepara os dicionários de respostas corretas e pesos
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
    somaDen = sum(peso_dict.values())
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

    # ========================================================================
    # ANOTAÇÃO NA IMAGEM – DESENHAR OS MARCADORES
    # Para cada pergunta, se a opção marcada for a correta (única), desenha um círculo verde;
    # caso contrário (resposta errada, ausente ou duplicada), desenha um círculo vermelho sobre a opção correta.
    option_mapping = {'A': 0, 'B': 1, 'C': 2, 'D': 3}
    for pergunta in sorted(respostas_corretas_dict.keys()):
        resposta_correta = respostas_corretas_dict[pergunta]
        if pergunta in marcadas_por_pergunta and marcadas_por_pergunta[pergunta] == resposta_correta:
            letra = marcadas_por_pergunta[pergunta]
            cor = (0, 255, 0)  # verde para correto
        else:
            letra = resposta_correta
            cor = (0, 0, 255)  # vermelho para incorreto ou não respondida
        label = f"{pergunta}-{letra}"
        if label in resp:
            index = resp.index(label)
            if index < len(campos):
                (x, y, w, h) = campos[index]
                center = (int(x + w/2), int(y + h/2))
                cv.circle(gabarito, center, 5, cor, -1)

    # Codifica a imagem anotada para base64
    retval, buffer = cv.imencode('.jpg', gabarito)
    jpg_as_text = base64.b64encode(buffer).decode('utf-8')
    result["imagem_resultado"] = "data:image/jpeg;base64," + jpg_as_text

    return result

@app.route('/api/app24/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "Nenhum arquivo enviado"}), 400

    file = request.files['file']
    respostas_corretas = request.form.get('respostas_corretas', '')
    peso = request.form.get('peso', '')

    if file.filename == '':
        return jsonify({"error": "Nenhum arquivo selecionado"}), 400

    respostas_corretas = respostas_corretas.split(',')
    if peso:
        peso = peso.split(',')
    else:
        peso = ['1'] * len(respostas_corretas)

    try:
        resultado = process_image(file.read(), respostas_corretas, peso)
        return jsonify(resultado)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(port=5002)