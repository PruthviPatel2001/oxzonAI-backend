from flask import request, jsonify, send_file
from db import mongo  
import os
import fitz
from bson.objectid import ObjectId

SEARCHED_FOLDER = os.path.join(os.getcwd(), 'highlightedFiles')


def search_document():
    try:
        search_term = request.json.get('search_term')
        document_id = request.json.get('document_id')
        
        if not search_term or not document_id:
            return jsonify({'error': 'Search term or document ID missing!'}), 400
        
        try:
            document_id = ObjectId(document_id)
        except Exception:
            return jsonify({'error': 'Invalid document ID format!'}), 400
        
        document = mongo.db.pdfData.find_one({"_id": document_id})
        if not document:
            return jsonify({'error': 'Document not found!'}), 404
        
        file_path = document['pdf_location']
        
        if not os.path.exists(file_path):
            return jsonify({'error': 'File not found on the server!'}), 404
        
        doc = fitz.open(file_path)
        occurrences = []
        total_occurrences = 0

        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            text_instances = page.search_for(search_term)
            
            if text_instances:
                occurrences.append({
                    'page': page_num + 1,
                    'count': len(text_instances),
                    'positions': [(inst.x0, inst.y0, inst.x1, inst.y1) for inst in text_instances]
                })
                total_occurrences += len(text_instances)
                
                for inst in text_instances:
                    highlight = page.add_highlight_annot(inst)
                    highlight.update()

        highlighted_filepath = os.path.join(SEARCHED_FOLDER, f'highlighted_{document["name"]}')
        doc.save(highlighted_filepath)
        doc.close()

        return jsonify({
            'total_occurrences': total_occurrences,
            'occurrences_by_page': occurrences,
            'highlighted_file': highlighted_filepath
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    

def download_highlighted_file():

    filename = request.args.get('filename')
    file_path = os.path.join(SEARCHED_FOLDER, filename)

    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    else:
        return jsonify({'error': 'File not found!'}), 404