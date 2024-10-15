from flask import Blueprint, request, jsonify
from db import mongo  
from bson.objectid import ObjectId

from services.documentUpload import upload_document
from services.keywordSearch import search_document, download_highlighted_file
from services.queryDocument import query_document_for_answer
from services.manageLargeDocuments import summarize_large_document

document_routes = Blueprint('document_routes', __name__)



@document_routes.route('/upload', methods=['POST'])
def upload_route():
    return upload_document(request)

@document_routes.route('/search', methods=['POST'])
def search_route():
    return search_document()

@document_routes.route('/download_highlighted_file', methods=['GET'])
def download_highlighted_file_route():
    return download_highlighted_file(request) 
    
@document_routes.route('/query-document', methods=['POST'])
def query_document_route():
    data = request.get_json()
    document_id = data.get('document_id')
    user_query = data.get('question')

    # Fetch the document from the database
    document = mongo.db.ReportDetails.find_one({"_id": ObjectId(document_id)})
    
    if not document:
        return jsonify({'error': 'Document not found!'}), 404

    # Check the document's page count
    if document and 'pages' in document and int(document['pages']) > 2 and ('summary' in user_query.lower() or 'summarize' in user_query.lower()):
        return summarize_large_document(document)  
    else:
        return query_document_for_answer(user_query, document)  


@document_routes.route('/summarize-large-doc', methods=['POST'])
def large_doc_summarize_route():
    return summarize_large_document()