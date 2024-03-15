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

columns = ['Score1', 'Score2', 'Sum', 'Matches']

df_results = pd.DataFrame(columns=columns)

df_results['Score1'] = df_results['Score1'].astype(float)
df_results['Score2'] = df_results['Score2'].astype(float)
df_results['Sum'] = df_results['Sum'].astype(float)
df_results['Matches'] = df_results['Matches'].astype(int)
compact_df = df.drop(df.columns[[0, 2, 4, -1]], axis=1)

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
    global df_results

    for index, row in compact_df.iterrows():
        df_results.loc[index, "Matches"] = 0
        for column, value in row.items():
            if pd.notna(value):
                name_without_accents = unidecode(value)
                values = name_without_accents.split(', ')
                for i in range(len(values)):
                    values[i] = values[i].replace(' ', '-')

                values = set(values)
                values_same = values.intersection(set_detected_ingre)
                values_no_match = values - set_detected_ingre
                # values_redundant = set_detected_ingre - values
                score = 100 - ((len(values_same) * df.loc[index, "Ingre_Score"]) - (len(values_no_match) * df.loc[index, "Ingre_Score"]))
                df_results.loc[index, "Matches"] = df_results.loc[index, "Matches"] + len(values_same)

                if column == "Ingredients":
                    df_results.loc[index, "Score1"] = score
                else:
                    df_results.loc[index, "Score2"] = len(values_same) * df.loc[index, "Second_Ingre_Score"]

            else:
                df_results.loc[index, "Score2"] = 0
    
    df_results["Matches"] = df_results["Matches"].astype(int)
    
    for index, row in df_results.iterrows():
        score_main = row['Score1']
        score_extra = row['Score2']

        if score_main != 0:
            sum = round(score_main - score_extra, 2)
        else:
            sum = score_main

        df_results.at[index, 'Sum'] = float(sum)
    
    first_column = df['Food']
    df_results = pd.concat([first_column, df_results], axis=1)

    min_sum_value = df_results['Sum'].min()
    min_sum_rows = df_results[df_results['Sum'] == min_sum_value]
    max_matches_index = min_sum_rows['Matches'].idxmax()

    df_sorted = df_results.sort_values(by='Sum')
    four_rows_with_min = df_sorted.head(4)
    indexes = []
    suggests = []
    for index, row in four_rows_with_min.iterrows():
        indexes.append(index)
    
    indexes.remove(max_matches_index)

    for idx in indexes:
        title = str(df.loc[idx, "Food"]) + " - Đặc sản " + str(df.loc[idx, "Province"])
        suggests.append(title)

    del first_column
    del df_sorted
    del four_rows_with_min
    
    predicted_food = df.loc[max_matches_index, "Food"]
    province = df.loc[max_matches_index, "Province"]
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