from flask import Blueprint, request, jsonify
from models.record import Record
from models.appointment import Appointment
from flask_jwt_extended import jwt_required, get_jwt_identity

records_api_blueprint = Blueprint('records_api',
                             __name__,
                             template_folder='templates')


@records_api_blueprint.route('/create', methods=['POST'])
@jwt_required
def create():
    params = request.json
    appointment_id = params.get("appointment_id")
    cholestrol_level = params.get("cholestrol_level")
    sugar_level = params.get("sugar_level")
    systolic_blood_pressure = params.get("systolic_blood_pressure")
    diastolic_blood_pressure = params.get("diastolic_blood_pressure")
    
    user = get_jwt_identity()
    patient_record = Record(cholestrol_level=cholestrol_level, sugar_level=sugar_level, systolic_blood_pressure=systolic_blood_pressure, 
    diastolic_blood_pressure=diastolic_blood_pressure, appointment_id=appointment_id)
    if patient_record.save():
        return jsonify({
                        "cholestrol_level": cholestrol_level,
                        "sugar_level": sugar_level,
                        "systolic_blood_pressure": systolic_blood_pressure,
                        "diastolic_blood_pressure": diastolic_blood_pressure
                        
                    })


