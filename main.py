from flask import Flask, request, jsonify
from keras.models import load_model
from PIL import Image, ImageOps
import numpy as np
from flask_cors import CORS
import base64, io, re
from unidecode import unidecode

# Disable scientific notation for clarity
np.set_printoptions(suppress=True)

# Load the model
model = load_model("keras_model.h5", compile=False)

# Load the labels
class_names = open("labels.txt", "r").readlines()

app = Flask(__name__)

CORS(app)  # Configuração do CORS

# Endpoint para previsão
@app.route("/predict", methods=["POST"])
def predict():
    # Obtém o array de imagens do corpo da solicitação
    image_data = request.json.get("base64Images")

    image_name_to_find = request.json.get("strongText")
    print(image_name_to_find)
    
    # Inicializa a lista para armazenar as previsões
    predictions = []
    
    # Itera sobre cada imagem no array
    for img_data in image_data:
        # Decodifica a string base64 para bytes
        image_bytes = base64.b64decode(img_data.split(',')[1])

        # Abre a imagem usando a função Image.open() e passa os bytes decodificados
        image = Image.open(io.BytesIO(image_bytes))

        size = (224, 224)

        # Remova o canal alfa da imagem se existir
        # Verifica se a imagem tem canal alfa (RGBA)
        if image.mode == 'RGBA':
            # Converte a imagem para o modo RGB, removendo o canal alfa
            image = image.convert('RGB')
        
        # Redimensiona a imagem para 224x224 e centraliza o corte
        image = ImageOps.fit(image, size, Image.Resampling.LANCZOS)
        
        # Converte a imagem em um array numpy
        image_array = np.asarray(image)
        
        # Normaliza a imagem
        normalized_image_array = (image_array.astype(np.float32) / 127.5) - 1
        
        # Cria o array de dados
        data = np.ndarray(shape=(1, 224, 224, 3), dtype=np.float32)
        data[0] = normalized_image_array
        
        # Faz a previsão usando o modelo
        prediction = model.predict(data)
        index = np.argmax(prediction)
        class_name = class_names[index].strip()
        confidence_score = prediction[0][index]

        # Expressão regular para encontrar "Camiseta" desconsiderando acentos e case
        padrao = re.compile(image_name_to_find, re.IGNORECASE)

        # Remove acentos da classe
        classe_sem_acentos = unidecode(class_name)
        # Verifica se a palavra "Camiseta" está presente na classe sem acentos
        if padrao.search(classe_sem_acentos):
            print("image_name_to_find: " + image_name_to_find + "class_name: " + class_name)
        
        # Adiciona a previsão à lista de previsões
        predictions.append({
            "class": class_name,
            "confidence_score": float(confidence_score),
            "finded": bool(padrao.search(classe_sem_acentos))
        })
    
    # Retorna as previsões como resposta
    return jsonify(predictions)

if __name__ == "__main__":
    app.run(debug=True)
