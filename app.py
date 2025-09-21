import os
import matplotlib
matplotlib.use('Agg')  # non-interactive backend

from flask import Flask, request, jsonify
from flask_cors import CORS
import re
import pickle
import numpy as np
import pandas as pd

# ===== Flask serve UI từ thư mục fontend_basic =====
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__, static_folder='fontend_basic', static_url_path="")
CORS(app)  # không bắt buộc khi cùng origin, nhưng để cũng không sao

@app.route("/")
def home():
    return app.send_static_file("index.html")

@app.route("/health")
def health():
    return jsonify(status="ok")

# ===== NLTK: tự tải khi thiếu (tránh LookupError khi deploy) =====
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import nltk
try:
    _ = stopwords.words('english')
except LookupError:
    nltk.download('stopwords')
try:
    _ = WordNetLemmatizer()  # wordnet có thể cần
    nltk.data.find('corpora/wordnet')
except LookupError:
    nltk.download('wordnet')

# ===== Tiền xử lý =====
def preprocess_comment(comment: str):
    try:
        comment = comment.lower().strip()
        comment = re.sub(r'\n', ' ', comment)
        comment = re.sub(r'[^A-Za-z0-9\s!?.,]', '', comment)

        sw = set(stopwords.words('english')) - {'not','but','however','no','yet'}
        comment = ' '.join([w for w in comment.split() if w not in sw])

        lem = WordNetLemmatizer()
        comment = ' '.join([lem.lemmatize(w) for w in comment.split()])
        return comment
    except Exception as e:
        print(f"Error in preprocessing comment: {e}")
        return comment

# ===== Load model/vectorizer với đường dẫn tuyệt đối =====
def load_model(model_path, vectorizer_path):
    try:
        with open(model_path, 'rb') as f:
            model = pickle.load(f)
        with open(vectorizer_path, 'rb') as f:
            vectorizer = pickle.load(f)
        return model, vectorizer
    except Exception as e:
        print(f"Error loading model/vectorizer: {e}")
        raise

MODEL_PATH = os.path.join(BASE_DIR, "lgbm_model.pkl")
VECT_PATH  = os.path.join(BASE_DIR, "tfidf_vectorizer.pkl")
model, vectorizer = load_model(MODEL_PATH, VECT_PATH)
print("Load model successfully.")

# ===== API predict =====
@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json(silent=True) or {}
    comments = data.get('comments')

    if not comments or not isinstance(comments, list):
        return jsonify({"error": "No comments provided"}), 400
    try:
        preprocessed = [preprocess_comment(c) for c in comments]
        X = vectorizer.transform(preprocessed).toarray()
        preds = model.predict(X).tolist()
        resp = [{"comment": c, "sentiment": p} for c, p in zip(comments, preds)]
        return jsonify(resp)
    except Exception as e:
        return jsonify({"error": f"Prediction failed: {str(e)}"}), 500

if __name__ == '__main__':
    # bạn đã map 8080:8080 trong Docker/Runner
    app.run(host='0.0.0.0', port=8080, debug=True)
