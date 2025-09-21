import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend before importing pyplot

from flask import Flask,request,jsonify,send_file
from flask_cors import CORS
import io
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import mlflow
import numpy as np
import re
import pandas as pd
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from mlflow.tracking import MlflowClient
import matplotlib.dates as mdates
import pickle

app = Flask(__name__)
CORS(app) # Enable CORS for all routes

# Define the preprocessing funtion
def preprocess_comment(comment:str):
    """Apply preprocessing transfromations to a comment."""
    try:
        #Convert to lower
        comment = comment.lower()

        #Remove trailing and leading witespaces
        comment = comment.strip()

        #Remove newline characters
        comment = re.sub(r'\n',' ',comment)

        # Remove non-alphanumeric characters, except punctuation
        comment = re.sub(r'[^A-Za-z0-9\s!?.,]', '', comment)

        #Remove stopwords but retain important ones for setiment analysis
        stop_words = set(stopwords.words('english')) - {'not','but','however','no','yet'}

        comment = ' '.join([word for word in comment.split() if word not in stop_words])

         # Lemmatize the words
        lemmatizer = WordNetLemmatizer()
        comment = ' '.join([lemmatizer.lemmatize(word) for word in comment.split()])

        return comment
    except Exception as e:
        print(f"Error in preprocessing comment: {e}")
        return comment
    
# Load the model and vectorizer from model registry and local storage
# def load_model_and_vectorizer(model_name,model_version,vectorizer_path):
#     #Set MLfow tracking URI to your server
#     mlflow.set_tracking_uri("http://ec2-44-243-129-37.us-west-2.compute.amazonaws.com:5000/")
#     client = MlflowClient()
#     model_uri = f"models:/{model_name}/{model_version}"
#     model = mlflow.pyfunc.load_model(model_uri)

#     with open(vectorizer_path, 'rb') as file:
#        vectorizer = pickle.load(file)
    
#     return model, vectorizer


# Initialize the model and vectorizer
# model, vectorizer = load_model_and_vectorizer("my_model", "1", "./tfidf_vectorizer.pkl")  # Update paths and versions as needed

def load_model(model_path, vectorizer_path):
    """Load the trained model."""
    try:
        with open(model_path, 'rb') as file:
            model = pickle.load(file)
        
        with open(vectorizer_path, 'rb') as file:
            vectorizer = pickle.load(file)
      
        return model, vectorizer
    except Exception as e:
        raise
# Initialize the model and vectorizer
model, vectorizer = load_model("./lgbm_model.pkl", "./tfidf_vectorizer.pkl")  
print("Load model seccessfully.")
@app.route('/')
def home():
    return "Wellcome to our flask api"

@app.route('/predict', methods=['POST'])
def predict():
    data = request.json
    comments = data.get('comments')
    print("i am the comment: ",comments)
    print("i am the comment type: ",type(comments))
    
    if not comments:
        return jsonify({"error": "No comments provided"}), 400

    try:
        # Preprocess each comment before vectorizing
        preprocessed_comments = [preprocess_comment(comment) for comment in comments]
        
        # Transform comments using the vectorizer
        transformed_comments = vectorizer.transform(preprocessed_comments)

        # Convert the sparse matrix to dense format
        dense_comments = transformed_comments.toarray()  # Convert to dense array
        
        # Make predictions
        predictions = model.predict(dense_comments).tolist()  # Convert to list
        
        # Convert predictions to strings for consistency
        # predictions = [str(pred) for pred in predictions]
    except Exception as e:
        return jsonify({"error": f"Prediction failed: {str(e)}"}), 500
    
    # Return the response with original comments and predicted sentiments
    response = [{"comment": comment, "sentiment": sentiment} for comment, sentiment in zip(comments, predictions)]
    return jsonify(response)



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)