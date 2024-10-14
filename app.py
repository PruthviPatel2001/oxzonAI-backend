from flask import Flask, jsonify
from routes.documents_route import document_routes
from db import init_app, mongo  # Import mongo here
from flask_cors import CORS
from dotenv import load_dotenv
import os

load_dotenv()


app = Flask(__name__)
CORS(app)
app.config["MONGO_URI"] = "mongodb+srv://patelpruthvi:#Pruthvi1202@docstoragecluster.jl8my.mongodb.net/knowledge_base_app?retryWrites=true&w=majority&tlsInsecure=true&appName=DocStorageCluster"

# Initialize the MongoDB connection
init_app(app)

app.register_blueprint(document_routes)

@app.route('/test-connection', methods=['GET'])
def test_connection():
    try:
        # Attempt to retrieve data from the 'pdfData' collection
        pdf_data = mongo.db.pdfData.find_one()
        if pdf_data:
            return jsonify({"message": "Connection successful!", "data": pdf_data}), 200
        else:
            return jsonify({"message": "Connected, but no data found in pdfData collection."}), 404
    except Exception as e:
        return jsonify({"message": "Connection failed!", "error": str(e)}), 500

@app.route('/')
def home():
    return "Welcome to the Knowledge-Based Search Retrieval System."

if __name__ == '__main__':
    app.run(debug=True)
