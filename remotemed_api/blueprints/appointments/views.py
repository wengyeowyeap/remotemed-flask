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
        return jsonify({
            "message": "Something went wrong.",
            "status": "failed"
        })

# @appointments_api_blueprint.route('/show', methods=['POST'])
# @jwt_required
# def show():
#     user = get_jwt_identity()
#     user_id = User.get_or_none(User.id==user["id"])
#     if user_id:
#         if user["role"]== "doctor":
#             current_date_time = datetime.datetime.now()
#             print(current_date_time)
#             appointments = Appointment.select().where(Appointment.doctor_id==user["id"])
#             print(appointments)
            








@appointments_api_blueprint.route('/edit/<id>', methods=['POST'])
def edit(id):
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

@appointments_api_blueprint.route('/delete/<id>', methods=['POST'])
def destroy(id):
    appointment = Appointment.get_or_none(Appointment.id==id)
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


