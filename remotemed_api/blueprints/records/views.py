from flask import Blueprint, request, jsonify
from models.appointment import Appointment
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.user import User
from models.record import Record
from models.role import Role
from models.user_role import UserRole
from remotemed_api.util.s3_helpers import upload_file_to_s3
from datetime import datetime
from werkzeug.utils import secure_filename
from models.patient_photo import Patient_Photo


records_api_blueprint = Blueprint('records_api',
                                  __name__,
                                  template_folder='templates')


@records_api_blueprint.route('/create', methods=['POST'])
@jwt_required
def create():
    appointment_id = request.form.get("appointment_id")
    cholestrol_level = request.form.get("cholestrol_level")
    sugar_level = request.form.get("sugar_level")
    systolic_blood_pressure = request.form.get("systolic_blood_pressure")
    diastolic_blood_pressure = request.form.get("diastolic_blood_pressure")

    online_user = get_jwt_identity()
    user = User.get_or_none(User.id == online_user['id'])

    if (user) and ("patient" in user.role): #need to be updated if allow guardian to create record
        patient_record = Record(cholestrol_level=cholestrol_level, sugar_level=sugar_level, systolic_blood_pressure=systolic_blood_pressure, diastolic_blood_pressure=diastolic_blood_pressure, appointment_id=appointment_id)
        if patient_record.save():
            response = {
                "message": f"Successfully created record.",
                "status": "success",
                "cholestrol level" : patient_record.cholestrol_level,
                "sugar level" : patient_record.sugar_level,
                "systolic_blood_pressure" : patient_record.systolic_blood_pressure,
                "diastolic_blood_pressure" : patient_record.diastolic_blood_pressure,
                "appointment_id": patient_record.appointment_id
            }
        else:
            return jsonify({
                "message": "Add record failed, please try again",
                "status": "failed"
            })
            # Image Upload Start
        images = []
        for i in range(int(request.form.get('image_count'))):
            image = request.files['image_files' + str(i)]
            caption = request.form.get('caption' + str(i))

            if 'image' not in image.mimetype:
                patient_record.delete_instance()
                return jsonify({
                    "message": "One or more of the uploaded files is not an image. Please try again",
                    "status": "failed"
                })
            else:
                file_extension = image.mimetype
                file_extension = file_extension.replace('image/', '.')
                image.filename = str(datetime.now()) + file_extension
                image.filename = secure_filename(image.filename)
                image_url = upload_file_to_s3(image, user.ic_number)
                upload_image = Patient_Photo(record_id=patient_record.id, image_url=image_url, caption=caption)

                if upload_image.save():
                    images.append({
                        "image_url": upload_image.full_image_url,
                        "caption": caption
                    })
                else:
                    patient_record.delete_instance()
                    return jsonify({
                        "message": "Image upload failed, please try again",
                        "status": "failed"
                    })
        response["images"] = images
    else:
        response = {
            "message": "User not found/ Only patient is allowed to create record.",
            "status": "failed"
        }
    return jsonify(response)


@records_api_blueprint.route('/show', methods=['GET'])
@jwt_required
def show():
    ic_number = request.args.get('ic_number')
    user = User.get_or_none(User.ic_number == ic_number)

    if user:
        if ("patient" in user.role) and ("guardian" in user.role):
            # my patient's record
            patient_list = user.my_patient
            my_patient_record = []            
            for i in range(len(patient_list)):
                patient = User.get_or_none(User.id == patient_list[i])
                my_patient_record.append({
                    patient.ic_number : patient.record
                })
            response = {
                "message": "successfully retrieve record!",
                "status": "success",
                "guardian's record": user.record,
                "my_patient_record": my_patient_record
            }
        elif ("patient" in role_name_list) or ("doctor" in role_name_list):
            response = {
                "record": user.record,
                "message": "successfully retrieve record!",
                "status": "success"
            }
        elif "guardian" in role_name_list:
            # my patient's record
            patient_list = user.my_patient
            my_patient_record = []            
            for i in range(len(patient_list)):
                patient = User.get_or_none(User.id == patient_list[i])
                my_patient_record.append({
                    patient.ic_number : patient.record
                })
            response = {
                "message": "successfully retrieve record!",
                "status": "success",
                "my_patient_record": my_patient_record
            }
        else:
            response = {
                "message": "Admin has no record.",
                "status": "failed"
            }
    else:
        response = {
            "message": "User not found",
            "status": "failed"
        }
    return jsonify(response)


@records_api_blueprint.route('/me', methods=['GET'])
@jwt_required
def me():
    online_user = get_jwt_identity()
    user = User.get_or_none(User.id == online_user['id'])

    if user:
        if ("patient" in user.role) and ("guardian" in user.role):
            # my patient's record
            patient_list = user.my_patient
            my_patient_record = []            
            for i in range(len(patient_list)):
                patient = User.get_or_none(User.id == patient_list[i])
                my_patient_record.append({
                    patient.ic_number : patient.record
                })
            response = {
                "message": "successfully retrieve record!",
                "status": "success",
                "guardian's record": user.record,
                "my_patient_record": my_patient_record
            }
        elif ("patient" in user.role) or ("doctor" in user.role):
            response = {
                "record": user.record,
                "message": "successfully retrieve record!",
                "status": "success"
            }
        elif "guardian" in user.role:
            # my patient's record
            patient_list = user.my_patient
            my_patient_record = []            
            for i in range(len(patient_list)):
                patient = User.get_or_none(User.id == patient_list[i])
                my_patient_record.append({
                    patient.ic_number : patient.record
                })
            response = {
                "message": "successfully retrieve record!",
                "status": "success",
                "my_patient_record": my_patient_record
            }
        else:
            response = {
                "message": "Admin has no record.",
                "status": "failed"
            }
    else:
        response = {
            "message": "User not found",
            "status": "failed"
        }
    return jsonify(response)


@records_api_blueprint.route('/search', methods=['GET'])
@jwt_required
def search():
    id = request.args.get("record_id")
    record = Record.get_or_none(Record.id == id)

    if record:
        return jsonify({
            "record_id": record.id,
            "appointment_id": record.appointment_id,
            "report": record.report,
            "prescription": record.prescription,
            "payment_amount": str(record.payment_amount),
            "paid": record.paid,
            "cholestrol_level": str(float(record.cholestrol_level)),
            "sugar_level": str(float(record.sugar_level)),
            "systolic_blood_pressure": str(float(record.systolic_blood_pressure)),
            "diastolic_blood_pressure": str(float(record.diastolic_blood_pressure)),
            "doctor_name": record.appointment.doctor.name,
            "doctor_ic": record.appointment.doctor.ic_number,
            "patient_name": record.appointment.patient.name,
            "patient_ic": record.appointment.patient.ic_number,
            "record_photo": record.photo
        })
    else:
        return jsonify({
            "message": "There is no such record.",
            "status": "failed"
        })


@records_api_blueprint.route('/edit', methods=['POST'])
@jwt_required
def edit():
    online_user = get_jwt_identity()
    user = User.get_or_none(User.id == online_user['id'])

    if user:
        if ("doctor" in user.role):
            update_record = Record.get_or_none(Record.id == request.json.get("record_id"))
            if update_record:
                update_record.report = request.json.get("report")
                update_record.prescription = request.json.get("prescription")
                if update_record.save():
                    response = {
                        "message": "Updated record successfully",
                        "status": "success",
                        "report": update_record.report,
                        "prescription": update_record.prescription
                    }
                else:
                    response = {
                        "message": "Record not saved",
                        "status": "failed"
                    }
            else:
                response = {
                    "message": "Record not found",
                    "status": "failed"
                }
        elif ("admin" in user.role):
            update_record = Record.get_or_none(Record.id == request.json.get("record_id"))
            if update_record:
                update_record.payment_amount = request.json.get("payment_amount")
                if update_record.save():
                    response = {
                        "message": "Updated record successfully",
                        "status": "success",
                        "updated_payment_amount": update_record.payment_amount
                    }
                else:
                    response = {
                        "message": "Record not saved",
                        "status": "failed"
                    }
            else:
                response = {
                    "message": "Record not found",
                    "status": "failed"
                }
        else:
            response = {
                "message": "User has no permission to this page",
                "status": "failed"
            }
    else:
        response = {
            "message": "User does not exist",
            "status": "failed"
        }
    return jsonify(response)
