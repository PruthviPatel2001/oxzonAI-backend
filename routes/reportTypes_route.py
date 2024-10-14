# routes/report_types_route.py

from flask import Blueprint, jsonify
from models.documentMetaData import ReportType  

report_types_routes = Blueprint('report_types_routes', __name__)

@report_types_routes.route('/report-types', methods=['GET'])
def get_report_types():
    try:
        report_types = ReportType.get_all()
        return jsonify(report_types), 200
    except Exception as e:
        return jsonify({"message": "Error fetching report types", "error": str(e)}), 500
