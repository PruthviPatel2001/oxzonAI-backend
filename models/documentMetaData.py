from db import mongo  

class ReportType:
    def __init__(self, name, description=None):
        self.name = name
        self.description = description

    def save_to_db(self):
        result = mongo.db.ReportType.insert_one({
            'report_id': self.name,
            'report_type': self.description
        })
        return result.inserted_id

    @staticmethod
    def get_all():
        report_types = list(mongo.db.ReportType.find())
        for report_type in report_types:
            report_type['_id'] = str(report_type['_id'])
        return report_types


class DocumentNote:
    def __init__(self, document_id, note):
        self.document_id = document_id  # Reference to the document
        self.note = note

    def save_to_db(self):
        result = mongo.db.DocumentNotes.insert_one({
            'document_id': self.document_id,
            'note': self.note
        })
        return result.inserted_id

class Document:
    def __init__(self, name, report_id, pages, pdf_location):
        self.name = name
        self.report_id = report_id
        self.pages = pages
        self.pdf_location = pdf_location

    def save_to_db(self):
        result = mongo.db.ReportDetails.insert_one({
            'name': self.name,
            'report_id': self.report_id,
            'pages': self.pages,
            'pdf_location': self.pdf_location
        })
        return result.inserted_id 
    

    
