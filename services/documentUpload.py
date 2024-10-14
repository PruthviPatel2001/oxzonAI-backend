from flask import jsonify
from werkzeug.utils import secure_filename
from models.document import Document
import os


ALLOWED_EXTENSIONS = {'pdf'}
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'clientFiles')

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

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
            
            document = Document(
                name=data.get('name'),
                type_of_report=data.get('type_of_report'),
                additional_notes=data.get('additional_notes'),
                pages=data.get('pages'),
                pdf_location=file_path
            )
            
            # Save the document to the database and retrieve the inserted ID
            document_id = document.save_to_db()
            
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
        return jsonify({'error': str(e)}), 500