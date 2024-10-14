from db import mongo  

class Document:
    def __init__(self, name, type_of_report, additional_notes, pages, pdf_location):
        self.name = name
        self.type_of_report = type_of_report
        self.additional_notes = additional_notes
        self.pages = pages
        self.pdf_location = pdf_location

    def save_to_db(self):
        result = mongo.db.pdfData.insert_one({
            'name': self.name,
            'type_of_report': self.type_of_report,
            'additional_notes': self.additional_notes,
            'pages': self.pages,
            'pdf_location': self.pdf_location
        })
        return result.inserted_id 
    
