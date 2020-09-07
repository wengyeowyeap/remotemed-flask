from flask import Blueprint, request, jsonify
from models.appointment import Appointment
from models.record import Record
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
    online_user = get_jwt_identity()
    user = User.get_or_none(User.id == online_user['id'])

    if "admin" not in user.role:
        return jsonify({
            "message": "401 Unauthorized (Only admin is allowed)",
            "status": "fail"
        })

    params = request.json
    doctor_ic = params.get("doctor_ic")
    patient_ic = params.get("patient_ic")
    start_datetime = params.get("start_datetime")
    end_datetime = params.get("end_datetime")

    doctor = User.get_or_none(User.ic_number == doctor_ic)
    patient = User.get_or_none(User.ic_number == patient_ic)
    if doctor and patient:
        new_appointment = Appointment(doctor_id=doctor.id, patient_id=patient.id, start_datetime=start_datetime, end_datetime=end_datetime)
        if new_appointment.save():
            response = {
                "message": "Successfully created an appointment",
                "status ": "success",
                "doctor_name": new_appointment.doctor.name,
                "doctor_ic": new_appointment.doctor.ic_number,
                "patient_name": new_appointment.patient.name,
                "patient_ic": new_appointment.patient.ic_number,
                "start_datetime": new_appointment.start_datetime,
                "end_datetime": new_appointment.end_datetime
            }
        else:
            response = new_appointment.error()
        return jsonify(response)
    else:
        return jsonify({
            "message": "Can't find doctor or patient",
            "status ": "fail",
        })

@appointments_api_blueprint.route('/edit', methods=['POST'])
@jwt_required
def edit():
    online_user = get_jwt_identity()
    user = User.get_or_none(User.id == online_user['id'])

    if "admin" not in user.role:
        return jsonify({
            "message": "401 Unauthorized (Only admin is allowed)",
            "status": "fail"
        })

    id = request.json.get("appointment_id")
    start_datetime = request.json.get("start_datetime")
    end_datetime = request.json.get("end_datetime")
    doctor_ic = request.json.get("doctor_ic")
    patient_ic = request.json.get("patient_ic")

    appointment = Appointment.get_or_none(Appointment.id == id)
    if appointment:
        start_datetime = request.json.get("start_datetime")
        end_datetime = request.json.get("end_datetime")
        doctor_ic = request.json.get("doctor_ic")
        patient_ic = request.json.get("patient_ic")

        doctor = User.get_or_none(User.ic_number == doctor_ic)
        patient = User.get_or_none(User.ic_number == patient_ic)

        if doctor == None or patient == None:
            return jsonify({
                "message": "Patient or doctor not found",
                "status": "fail"
            }) 

        appointment.doctor = doctor
        appointment.patient = patient
        appointment.start_datetime = start_datetime
        appointment.end_datetime = end_datetime

        if appointment.save():
            response = {
                "message": "successfully changed appointment's info!",
                "status": "success",
                "patient_name": appointment.patient.name,
                "doctor_name": appointment.doctor.name,
                "patient_ic": appointment.patient.ic_number,
                "doctor_ic": appointment.doctor.ic_number,
                "start_datetime": appointment.start_datetime,
                "end_datetime": appointment.end_datetime
            }
        else:
            response = appointment.error()
    else:
        response ={
            "message": "Appointment not found.",
            "status": "fail"
        }
    return jsonify(response)

@appointments_api_blueprint.route('/me', methods=['GET'])
@jwt_required
def me():
    online_user = get_jwt_identity()
    user = User.get_or_none(User.id == online_user["id"])
    if user:
        if ("guardian" in user.role) and ("patient" in user.role):
            patient_list = user.my_patient
            my_patient_appointment = []
            for i in range(len(patient_list)):
                p = User.get_or_none(User.id == patient_list[i])
                my_patient_apppointment.append(
                    {
                    "patient_name": p.name,
                    "patient_ic": p.ic,
                    "upcoming": p.upcoming_appointment,
                    "past": p.past_appointment
                    }
                )
            response = {
                "status": "success",
                "my_appointment": {
                    "upcoming": user.upcoming_appointment,
                    "past": user.past_appointment
                },
                "my_patient_appointment": my_patient_appointment
            }          
        elif ("guardian" in user.role):
            patient_list = user.my_patient
            my_patient_appointment = []
            for i in range(len(patient_list)):
                p = User.get_or_none(User.id == patient_list[i])
                my_patient_apppointment.append(
                    {
                    "patient_name": p.name,
                    "patient_ic": p.ic,
                    "upcoming": p.upcoming_appointment,
                    "past": p.past_appointment
                    }
                )
            if my_patient_appointment:
                response = {
                    "status": "success",
                    "my_patient_appointment": my_patient_appointment
                }
            else:
                response = {
                    "status": "success",
                    "message": "There's no appointment for this guardian's patient."
                }                
        elif ("doctor" in user.role) or ("patient" in user.role):
            if user.upcoming_appointment or user.past_appointment:
                response = {
                    "status": "success",
                    "upcoming": user.upcoming_appointment,
                    "past": user.past_appointment
                }
            else:
                response = {
                    "status": "success",
                    "message": "There's no appointment for this user."
                }                    
        elif ("admin" in user.role):
            response = {
                "status": "fail",
                "message": "Admin has no appointment."
            }            
    else:
        response = {
            "status": "fail",
            "message": "User not found."
        }
    return jsonify(response)

@appointments_api_blueprint.route('/show', methods=['GET'])
@jwt_required
def show():
    ic_number = request.args.get("ic_number")
    user = User.get_or_none(User.ic_number == ic_number)

    if user:
        if ("guardian" in user.role) and ("patient" in user.role):
            patient_list = user.my_patient
            my_patient_appointment = []
            for i in range(len(patient_list)):
                p = User.get_or_none(User.id == patient_list[i])
                my_patient_appointment.append(
                    {
                    "patient_name": p.name,
                    "patient_ic": p.ic_number,
                    "upcoming": p.upcoming_appointment,
                    "past": p.past_appointment
                    }
                )
            response = {
                "status": "success",
                "my_appointment": {
                    "upcoming": user.upcoming_appointment,
                    "past": user.past_appointment
                },
                "my_patient_appointment": my_patient_appointment
            }          
        elif ("guardian" in user.role):
            patient_list = user.my_patient
            my_patient_appointment = []
            for i in range(len(patient_list)):
                p = User.get_or_none(User.id == patient_list[i])
                my_patient_appointment.append(
                    {
                    "patient_name": p.name,
                    "patient_ic": p.ic_number,
                    "upcoming": p.upcoming_appointment,
                    "past": p.past_appointment
                    }
                )
            if my_patient_appointment:
                response = {
                    "status": "success",
                    "my_patient_appointment": my_patient_appointment
                }
            else:
                response = {
                    "status": "success",
                    "message": "There's no appointment for this guardian's patient."
                }                
        elif ("doctor" in user.role) or ("patient" in user.role):
            if user.upcoming_appointment or user.past_appointment:
                response = {
                    "status": "success",
                    "upcoming": user.upcoming_appointment,
                    "past": user.past_appointment
                }
            else:
                response = {
                    "status": "success",
                    "message": "There's no appointment for this user."
                }                    
        elif ("admin" in user.role):
            response = {
                "status": "fail",
                "message": "Admin has no appointment."
            }            
    else:
        response = {
            "status": "fail",
            "message": "User not found."
        }
    return jsonify(response)

@appointments_api_blueprint.route('/search', methods=['GET'])
@jwt_required
def search():
    id = request.args.get("appointment_id")
    appointment = Appointment.get_or_none(Appointment.id == id)
    if appointment:
        if appointment.zoom_url:
            zoom_link = a.zoom_url
        else:
            zoom_link = None
        return jsonify({
            "appointment_id": appointment.id,
            "doctor_name": appointment.doctor.name,
            "patient_name": appointment.patient.name,
            "doctor_ic": appointment.doctor.ic_number,
            "patient_ic": appointment.patient.ic_number,
            "appointment_start": appointment.start_datetime.strftime("%Y-%m-%d %H:%M:%S"),
            "appointment_end": appointment.end_datetime.strftime("%Y-%m-%d %H:%M:%S"),
            "zoom_link": zoom_link
        })
    else:
        return jsonify({
            "message": "Appointment not found.",
            "status": "fail"
        })

@appointments_api_blueprint.route('/delete', methods=['POST'])
def destroy():
    online_user = get_jwt_identity()
    user = User.get_or_none(User.id == online_user['id'])

    if "admin" not in user.role:
        return jsonify({
            "message": "401 Unauthorized (Only admin is allowed)",
            "status": "fail"
        })

    id = request.json.get("appointment_id")
    appointment = Appointment.get_or_none(Appointment.id == id)
    if appointment:
        if appointment.delete_instance():
            return jsonify({
                "message": "Successfully deleted appointment.",
                "status": "success"
            })
        else:
            return jsonify({
                "message": "Couldn't delete appointment.",
                "status": "fail"
            })
    else:
        return jsonify({
            "message": "No such appointment exists.",
            "status": "fail"
        })


@appointments_api_blueprint.route('/get_zoom_url', methods=['GET'])
@jwt_required
def get_zoom_url():
    import json
    from zoomus import ZoomClient
    from zoomus.components import meeting
    from app import app

    client = ZoomClient(app.config.get('ZOOM_API_KEY'), app.config.get('ZOOM_API_SECRET'))

    user_list_response = client.user.list()
    user_list = json.loads(user_list_response.content)

    for user in user_list['users']:
        user_id = user['id']
        print(json.loads(client.meeting.list(user_id=user_id).content))

    new_meeting = client.meeting.create(user_id=user_id).json()
    join_url = new_meeting['join_url']

    id = request.args.get('appointment_id')
    appointment = Appointment.get_or_none(Appointment.id == id)

    appointment.zoom_url = join_url
    appointment.start_datetime = appointment.start_datetime.strftime("%Y-%m-%d %H:%M:%S")
    appointment.end_datetime = appointment.end_datetime.strftime("%Y-%m-%d %H:%M:%S")
    if appointment.save():
        return join_url
    else:
        return "fail"
