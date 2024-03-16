from ultralytics import YOLO
import cv2
import base64
import pandas as pd
import matplotlib.pyplot as plt
from flask import Flask, jsonify
from flask_cors import CORS, cross_origin
from flask import request
from unidecode import unidecode

app = Flask(__name__)

# Set up module
classes_path = './assets/classes.txt'
ingredients_path = './assets/ingredients_name.txt'
excel_file_path = './assets/Chi_Tiet_Mon_An.xlsx'

detect_model = YOLO('./assets/yolo_detect_85.pt')
df = pd.read_excel(excel_file_path)
classes_ingre = []

with open(classes_path, 'r', encoding='utf-8') as file:
    lines = [line.strip() for line in file]
    classes_ingre = lines

with open(ingredients_path, 'r', encoding='utf-8') as f:
    ingredients = f.read().splitlines()

compact_df = df.drop(df.columns[[0, -1]], axis=1)

CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

def show_img(img):
    # Convert BGR to RGB
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    plt.imshow(img)
    plt.title("Detected Objects")
    plt.show()

def find_class(set_detected_ingre):
    global compact_df

    distances = []
    size_ingre = []
    matches = []

    for index, row in compact_df.iterrows():
        distance = 0
        size = 0
        for column, value in row.items():
            if pd.notna(value):
                name_without_accents = unidecode(value)
                values = name_without_accents.split(', ')
                for i in range(len(values)):
                    values[i] = values[i].replace(' ', '-')

                values = set(values)
                size = len(values)
                values_match = values.intersection(set_detected_ingre)
                # values_no_match = values - set_detected_ingre
                # values_redundant = set_detected_ingre - values

                if column == "Ingredients":
                    for element in set_detected_ingre:
                        if element in values:
                            distance = distance + 0
                        else:
                            distance = distance + 1
                else:
                    for element in set_detected_ingre:
                        if element in values:
                            distance = distance + 0.5
        distances.append(distance)
        size_ingre.append(size)
        matches.append(len(values_match))

    # print("New element:", set_detected_ingre)
    # print(distances, len(distances))
    # print(size_ingre, len(size_ingre))
    # print(matches, len(matches))
    min_value = min(distances)
    smallest_values_list = [index for index, elem in enumerate(distances) if elem == min_value]

    minus = []
    for index in smallest_values_list:
        subtraction = abs(size_ingre[index] - matches[index])
        minus.append(subtraction)

    # print(minus)
    minus_min = min(minus)
    min_index = minus.index(minus_min)
    min_index = smallest_values_list[min_index]
    # print("Predicted Food: " + df.loc[min_index, "Food"] + " - Đặc sản " + str(df.loc[min_index, "Province"]))

    sorted_indices = sorted(range(len(distances)), key=lambda i: distances[i])[:4]
    sorted_indices.pop(0)
    suggests = []

    for i in sorted_indices:
        title = str(df.loc[i, "Food"]) + " - Đặc sản " + str(df.loc[i, "Province"])
        suggests.append(title)
    
    predicted_food = df.loc[min_index, "Food"]
    province = df.loc[min_index, "Province"]
    return predicted_food, province, suggests

def draw_bouding_box(image, boxes, detected_cls, names):
    for index, (box, cls) in enumerate(zip(boxes, detected_cls)):
        x1, y1, x2, y2 = box

        color = (255, 0, 0)
        left, top, right, bottom = int(x1), int(y1), int(x2), int(y2)
        label = names.get(int(cls))

        cv2.rectangle(image, (left, top), (right, bottom), (0, 255, 0), 1)
        text_color = (255, 255, 255) # white color
        bg_color = (0, 255, 0)
        image[top - 15:top, left:right, :] = bg_color
        cv2.putText(image, label, (left, top - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, text_color, 2)
    
    return image


@app.route('/api/predict', methods=['POST'])
@cross_origin(origins='*')
def predict_food():
    global ingredients
    global classes_ingre

    uploaded_file = request.files['file']
    uploaded_file = cv2.imread(uploaded_file)
    results = detect_model(uploaded_file, save=False, project='yolo_results')

    boxes = results[0].boxes.xyxy.tolist()
    names = results[0].names
    detected_cls = results[0].boxes.cls.tolist()
    detected_normalized = results[0].boxes.cls.tolist()

    img = draw_bouding_box(uploaded_file, boxes, detected_cls, names)

    for i in range(len(detected_cls)):
        idx = int(detected_cls[i])
        detected_cls[i] = ingredients[idx]
        detected_normalized[i] = classes_ingre[idx]
    
    _, encoded_image = cv2.imencode('.jpg', img)
    encoded_image = base64.b64encode(encoded_image).decode('utf-8')

    predicted_food, province, suggests = find_class(set(detected_normalized))
    
    return jsonify({
        'detected_image': encoded_image,
        'detected_classes': detected_cls,
        'food_name': predicted_food,
        'suggest_others': suggests,
        'province': province
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port='9999')