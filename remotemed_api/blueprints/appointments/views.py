from flask import Blueprint, request, jsonify
from models.appointment import Appointment
from models.user import User
from models.user_role import UserRole
from models.role import Role
from flask_jwt_extended import jwt_required, get_jwt_identity
import datetime

appointments_api_blueprint = Blueprint('appointments_api',
                             __name__,
                             template_folder='templates')


@appointments_api_blueprint.route('/create', methods=['POST'])
@jwt_required
def create():
    params = request.json
    doctor_id = params.get("doctor_id")
    patient_id = params.get("patient_id")
    start_datetime = params.get("start_datetime")
    end_datetime = params.get("end_datetime")
    
    new_appointment = Appointment(doctor_id=doctor_id, patient_id=patient_id, start_datetime=start_datetime, end_datetime=end_datetime)
    if new_appointment.save():
        return jsonify({
            "message": "Successfully created an appointment",
            "status ": "success",
            "doctor_id": doctor_id,
            "patient_id": patient_id,
            "start_datetime": start_datetime,
            "end_datetime": end_datetime
        })
    else:
        error_msg = []
        for err in new_appointment.errors:
            error_msg.append(err)
        response = {
            "message": error_msg,
            "status": "failed"
        }
        return jsonify(response)

@appointments_api_blueprint.route('/me', methods=['GET'])
@jwt_required
def me():
    user = get_jwt_identity()
    user_id = User.get_or_none(User.id==user["id"])
    if user_id:
        if "doctor" in user["role"]:
            current_date_time = datetime.datetime.now()
            appointments = Appointment.select().where(Appointment.doctor_id==user["id"])
            doctor_records = []
            if appointments:
                response={
                    "message": "There is no upcoming appointment.",
                    "status": "success"
                }
                for a in appointments:
                    enddatetime = a.end_datetime
                    if enddatetime > current_date_time:
                        response["message"] = "Successfully retrieve appointment!"
                        doctor_records.append({
                        "appointment_id": a.id,
                        "doctor_id": a.doctor_id,
                        "patient_id": a.patient_id,
                        "appointment_time": a.start_datetime
                        })
                response["doctor_records"] = doctor_records
                return jsonify(response)
            else:
                return jsonify({
                    "message": "This doctor has no upcoming appointment.",
                    "status": "success"
                })

        elif "patient" in user["role"] and "guardian" in user["role"]:
            current_date_time = datetime.datetime.now()
            patients = User.select().where(User.guardian_id==user["id"])
            patient_list = []
            for p in patients:
                patient_list.append(p.id)
                print(patient_list)
            response={
                        "message": "There is no upcoming appointment.",  #Line1 - This line will be replaced if there is an apponitment afterward.
                        "status": "success"
                    }
            patient_records = []
            guardian_record = []  
            for patient_id in patient_list:
                print(patient_id)
                appointments = Appointment.select().where(Appointment.patient_id==patient_id) + Appointment.select().where(Appointment.patient_id==user["id"])
                if appointments:
                    for a in appointments:
                        enddatetime = a.end_datetime
                        if enddatetime > current_date_time:
                            if a.patient_id==patient_id:
                                response["message"] = "Successfully retrieve appointment!"
                                patient_records.append({
                                "appointment_id": a.id,
                                "doctor_id": a.doctor_id,
                                "patient_id": a.patient_id,
                                "appointment_time": a.start_datetime
                            })
                            else:
                                response["message"] = "Successfully retrieve appointment!"
                                guardian_record.append({
                                "appointment_id": a.id,
                                "doctor_id": a.doctor_id,
                                "patient_id": a.patient_id,
                                "appointment_time": a.start_datetime
                            })
                    response["patient_records"] = patient_records
                    response["guardian_record"] = guardian_record
                    return jsonify(response)
                else:
                    return jsonify({
                    "message": "This doctor has no upcoming appointment.",
                    "status": "success"
                })   
        elif "patient" in user["role"]:
            current_date_time = datetime.datetime.now()
            appointments = Appointment.select().where(Appointment.patient_id==user["id"])
            patient_record = []
            if appointments:
                response={
                "message": "There is no upcoming appointment.",
                "status": "success"
                }
                for a in appointments:
                    enddatetime = a.end_datetime
                    if enddatetime > current_date_time:
                        response["message"] = "Successfully retrieve appointment!"
                        patient_record.append({
                        "appointment_id": a.id,
                        "doctor_id": a.doctor_id,
                        "patient_id": a.patient_id,
                        "appointment_time": a.start_datetime
                    })
                response["patient_record"] = patient_record
                return jsonify(response)
            else:
                return jsonify({
                    "message": "This doctor has no upcoming appointment.",
                    "status": "success"
                }) 
        
        elif "guardian" in user["role"]:
            current_date_time = datetime.datetime.now()
            patients = User.select().where(User.guardian_id==user["id"])
            patient_list = []
            for p in patients:
                patient_list.append(p.id)
            response={
                "message": "There is no upcoming appointment.",
                "status": "success"
            }
            records = []
            for p_id in patient_list:
                appointments = Appointment.select().where(Appointment.patient_id==p_id)
                if appointments:
                    for a in appointments:
                        enddatetime = a.end_datetime
                        if enddatetime > current_date_time:
                            response["message"] = "Successfully retrieve appointment!"
                            records.append({
                            "appointment_id": a.id,
                            "doctor_id": a.doctor_id,
                            "patient_id": a.patient_id,
                            "appointment_time": a.start_datetime
                            })
                        
                    response["patient's record"] = records
                    return jsonify(response)
                else:
                    return jsonify({
                    "message": "There is no upcoming appointment.",
                    "status": "success"
                })
        else:
            return jsonify({
                "message": "This user has no upcoming appointment.",
                "status": "success"
                })
            
@appointments_api_blueprint.route('/show', methods=['GET'])
@jwt_required
def show():
    ic_number = request.json.get("ic_number")
    verified_user = User.get_or_none(User.ic_number==ic_number)
    current_date_time = datetime.datetime.now()
    if verified_user:
        appointments = Appointment.select().where(Appointment.patient_id==verified_user.id)
        if appointments:
            response={
                "message": "There is no upcoming appointment.",
                "status": "success"
            }
            all_list = []
            upcoming_list = []
            for a in appointments:
                enddatetime = a.end_datetime    
                response["message"] = "Successfully retrieve appointment!"
                all_list.append({
                    "appointment_id": a.id,
                    "doctor_id": a.doctor_id,
                    "patient_id": a.patient_id,
                    "appointment_time": a.start_datetime
                })
                
                if enddatetime > current_date_time:
                    response["message"] = "Successfully retrieve appointment!"
                    upcoming_list.append({
                    "appointment_id": a.id,
                    "doctor_id": a.doctor_id,
                    "patient_id": a.patient_id,
                    "appointment_time": a.start_datetime
                    })
            
            response["all_list"] = all_list
            response["upcoming_list"] = upcoming_list
            return jsonify(response)
        else:
            return jsonify({
                "message": "There is no appointment.",
                "status": "success"
            })
    else:
        return jsonify({
            "message": "There is no such user.",
            "status": "failed"
            })
            

@appointments_api_blueprint.route('/edit', methods=['POST'])
def edit():
    id = request.json.get("appointment_id")
    appointment = Appointment.get_or_none(Appointment.id==id)
    if appointment:
        params = request.json
        start_datetime = params.get("start_datetime")
        end_datetime = params.get("end_datetime")
        doctor_id = params.get("doctor_id")
        patient_id = params.get("patient_id")

        appointment.doctor_id = doctor_id
        appointment.patient_id = patient_id
        appointment.start_datetime = start_datetime
        appointment.end_datetime = end_datetime

        if appointment.save():
            return jsonify({
                "message": "successfully changed appointment's info!",
                "status": "success",
                "patient_id": patient_id,
                "doctor_id": doctor_id,
                "start_datetime": start_datetime,
                "end_datetime": end_datetime
            })
        else:
            return jsonify({
                "message": "Appointment couldn't be edited",
                "status": "failed"
            })
    else:
        return jsonify({
            "message": "No such appointment exists.",
            "status": "failed"
        })

@appointments_api_blueprint.route('/delete', methods=['POST'])
def destroy():
    id = request.json.get("appointment_id")
    appointment = Appointment.get_or_none(Appointment.id==id)
    if appointment:
        if appointment.delete_instance():
            return jsonify({
                "message": "Successfully deleted appointment.",
                "status": "success"
            })
        else:
            return jsonify({
                "message": "Couldn't delete appointment.",
                "status": "failed"
            })
    else:
        return jsonify({
            "message": "No such appointment exists.",
            "status": "failed"
        })


