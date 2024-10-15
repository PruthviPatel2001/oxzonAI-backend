import uuid
from flask import jsonify
from werkzeug.utils import secure_filename
from models.documentMetaData import Document, DocumentNote, DocumentEmbedding
import os
from sentence_transformers import SentenceTransformer
import fitz  # PyMuPDF for PDF text extraction
import numpy as np
import hashlib
from utils.generate_embedding import generate_embedding
from utils.setupForFAISS import add_embeddings_to_faiss, initialize_faiss_index

# Initialize the Sentence-Transformer model
embedding_model = SentenceTransformer('paraphrase-MiniLM-L6-v2')

ALLOWED_EXTENSIONS = {'pdf'}
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'clientFiles')

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# def generate_embedding(text):
#     """Generate embedding for the given text using Sentence Transformers."""
#     try:
#         # Generate embedding for the document text
#         embedding = embedding_model.encode(text)
        
#         # Ensure the embedding is a list (convert from numpy array)
#         if isinstance(embedding, np.ndarray):
#             embedding = embedding.tolist()

#         return embedding
#     except Exception as e:
#         print(f"Error generating embedding: {e}")
#         return None

def extract_text_from_pdf(pdf_path):
    """Extract text from the given PDF using PyMuPDF."""
    try:
        doc = fitz.open(pdf_path)
        full_text = ""
        
        for page in doc:
            full_text += page.get_text()

        return full_text
    except Exception as e:
        print(f"Error extracting text from PDF: {e}")
        return ""

def upload_document(request):
    try:
        # Check if 'file' is in the request
        if 'file' not in request.files:
            return jsonify({'error': 'No file part in the request'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            file.save(file_path)
            
            data = request.form
            
            # Create Document instance
            document = Document(
                name=data.get('name'),
                report_id=data.get('report_id'),
                pages=data.get('pages'),
                pdf_location=file_path
            )
            
            # Save the document to the database and retrieve the inserted ID
            document_id = document.save_to_db()
            
            # Save additional notes, if provided
            additional_notes = data.get('additional_notes')
            if additional_notes:
                note = DocumentNote(document_id=document_id, note=additional_notes)
                note.save_to_db() 

            # Extract document text
            document_text = extract_text_from_pdf(file_path)

            if not document_text:
                return jsonify({'error': 'Failed to extract text from the PDF'}), 500

            # Generate the embedding for the document content
            embedding_faiss, embedding_mongo = generate_embedding(document_text)
            
            # If embedding generation was successful, save the embedding to the database
            if embedding_faiss is not None and embedding_mongo is not None:
                # Save the embedding to MongoDB
                document_embedding = DocumentEmbedding(document_id=document_id, embedding=embedding_mongo)
                document_embedding.save_to_db()

                # Add the embedding to FAISS index
                faiss_index = initialize_faiss_index()
                if faiss_index is not None:
                    # Convert the ObjectId to a hash and use it as an integer ID for FAISS
                    faiss_id = uuid.uuid5(uuid.NAMESPACE_OID, str(document_id)).int & ((1 << 63) - 1)
                    add_embeddings_to_faiss(faiss_index, [embedding_faiss], [faiss_id])
                else:
                    return jsonify({'error': 'Error initializing FAISS index'}), 500
            else:
                return jsonify({'error': 'Failed to generate embedding for the document'}), 500

            # Convert ObjectId to string before returning it in the response
            return jsonify({
                'message': 'Document uploaded successfully!',
                'file_path': file_path,
                'document_name': data.get('name'),
                'document_id': str(document_id)
            }), 201
        else:
            return jsonify({'error': 'File extension not allowed. Please upload a PDF file.'}), 400
    
    except Exception as e:
        print(f"Error in document upload process: {e}")
        return jsonify({'error': str(e)}), 500