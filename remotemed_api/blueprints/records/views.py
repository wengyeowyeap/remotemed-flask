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
    appointment_id = request.json.get("appointment_id")
    cholestrol_level = request.form.get("cholestrol_level")
    sugar_level = request.form.get("sugar_level")
    systolic_blood_pressure = request.form.get("systolic_blood_pressure")
    diastolic_blood_pressure = request.form.get("diastolic_blood_pressure")
    
    online_user = get_jwt_identity()
    user = User.get_or_none(User.id == online_user['id'])

    good_response = {
                "message": f"Successfully created record.",
                "status": "success",
            }

    if user:
        patient_record = Record(cholestrol_level=cholestrol_level, sugar_level=sugar_level, systolic_blood_pressure=systolic_blood_pressure, 
        diastolic_blood_pressure=diastolic_blood_pressure, appointment_id=appointment_id)
        if patient_record.save():
            good_response["cholestrol level"] = cholestrol_level
            good_response["sugar level"] = sugar_level
            good_response["systolic_blood_pressure"] = systolic_blood_pressure
            good_response["diastolic_blood_pressure"] = diastolic_blood_pressure
        else:
            return jsonify({
                "message": "Add record failed, please try again",
                "status": "failed"
            })
            #Image Upload Start
        images = []
        for i in range(int(request.form.get('image_count'))):
            image = request.files['image_files'+ str(i)]
            caption = request.form.get('caption'+ str(i))

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
                upload_image = Patient_Photo(record_id = 1, image_url = image_url, caption = caption)
                
                if upload_image.save():
                    images.append({
                        "image_url" : upload_image.full_image_url,
                        "caption" : caption
                    })
                    good_response["images"] = images
                else:
                    patient_record.delete_instance()
                    return jsonify({
                        "message": "Image upload failed, please try again",
                        "status": "failed"
                    })
        return jsonify(good_response)
    else:
        return jsonify({
                        "message": "Image upload failed, please try again",
                        "status": "failed"
                    })
    

@records_api_blueprint.route('/show', methods=['GET'])
@jwt_required
def show():
    ic_number = request.args.get('ic_number')
    user = User.get_or_none(User.ic_number == ic_number)

    if user:
        role_list = Role.select().join(UserRole).where(UserRole.user_id == user.id) #select all existing role(s)
        role_name_list = []
        for r in role_list:
            role_name_list.append(r.role_name)
        if ("patient" in role_name_list) and ("guardian" in role_name_list):
            response={
                        "message": "successfully retrieve record!",
                        "status": "success"
                    }
            #my patient's record
            p_list = User.select().where(User.guardian_id==user.id)
            if p_list:
                patient_list = []
                for p in p_list:
                    patient_list.append(p.id)
                my_patient_record = []
                for i in range(len(patient_list)):
                    p_record = Record.select().join(Appointment).where(Appointment.patient_id == patient_list[i])
                    if p_record:
                        for r in p_record:
                            appointment = Appointment.get_or_none(Appointment.id == r.appointment_id)
                            my_patient_record.append({
                                    "record_id": r.id,
                                    "appointment_id": r.appointment_id,
                                    "report": r.report,
                                    "prescription": r.prescription,
                                    "payment_amount": str(r.payment_amount),
                                    "paid": r.paid,
                                    "cholestrol_level": str(r.cholestrol_level),
                                    "sugar_level": str(r.sugar_level),
                                    "systolic_blood_pressure": r.systolic_blood_pressure,
                                    "diastolic_blood_pressure": r.diastolic_blood_pressure,
                                    "doctor_id" : appointment.doctor_id,
                                    "patient_id" : appointment.patient_id                                    
                                    }
                            )
                        response["my_patient_record"] = my_patient_record
                    else:
                        response["my_patient_record"] = []
            #My own record
            record_list = Record.select().join(Appointment).where(Appointment.patient_id == user.id)
            guardian_record = []
            if record_list:
                for r in record_list:
                    appointment = Appointment.get_or_none(Appointment.id == r.appointment_id)
                    guardian_record.append({
                            "record_id": r.id,
                            "appointment_id": r.appointment_id,
                            "report": r.report,
                            "prescription": r.prescription,
                            "payment_amount": str(r.payment_amount),
                            "paid": r.paid,
                            "cholestrol_level": str(r.cholestrol_level),
                            "sugar_level": str(r.sugar_level),
                            "systolic_blood_pressure": r.systolic_blood_pressure,
                            "diastolic_blood_pressure": r.diastolic_blood_pressure,
                            "doctor_id" : appointment.doctor_id,
                            "patient_id" : appointment.patient_id                            
                        }
                    )
                    
                response["guardian_record"] = guardian_record 
                print(response)
            else:
                response["guardian_record"] = []     
        elif "patient" in role_name_list:
            record_list = Record.select().join(Appointment).where(Appointment.patient_id == user.id)
            my_patient_record = []
            if record_list:
                for r in record_list:
                    appointment = Appointment.get_or_none(Appointment.id == r.appointment_id)
                    my_patient_record.append({
                            "record_id": r.id,
                            "appointment_id": r.appointment_id,
                            "report": r.report,
                            "prescription": r.prescription,
                            "payment_amount": str(r.payment_amount),
                            "paid": r.paid,
                            "cholestrol_level": str(r.cholestrol_level),
                            "sugar_level": str(r.sugar_level),
                            "systolic_blood_pressure": r.systolic_blood_pressure,
                            "diastolic_blood_pressure": r.diastolic_blood_pressure,
                            "doctor_id" : appointment.doctor_id,
                            "patient_id" : appointment.patient_id
                        }                        
                    )
                response = {
                            "my_patient_record": my_patient_record,
                            "message": "successfully retrieve record!",
                            "status": "success"
                        }
            else:
                response["patient_record"] = []
        elif "doctor" in role_name_list:
            record_list = Record.select().join(Appointment).where(Appointment.doctor_id == user.id)
            doctor_record = []
            if record_list:
                for r in record_list:
                    appointment = Appointment.get_or_none(Appointment.id == r.appointment_id)
                    doctor_record.append({
                            "record_id": r.id,
                            "appointment_id": r.appointment_id,
                            "report": r.report,
                            "prescription": r.prescription,
                            "payment_amount": str(r.payment_amount),
                            "paid": r.paid,
                            "cholestrol_level": str(r.cholestrol_level),
                            "sugar_level": str(r.sugar_level),
                            "systolic_blood_pressure": r.systolic_blood_pressure,
                            "diastolic_blood_pressure": r.diastolic_blood_pressure,
                            "doctor_id" : appointment.doctor_id,
                            "patient_id" : appointment.patient_id                            
                        }
                    )
                response = {
                            "doctor_record": doctor_record,
                            "message": "successfully retrieve record!",
                            "status": "success"
                        }
            else:
                response["doctor_record"] = [] 
        elif "guardian" in role_name_list:
            #my patient's record
            p_list = User.select().where(User.guardian_id==user.id)
            if p_list:
                patient_list = []
                for p in p_list:
                    patient_list.append(p.id)
                my_patient_record = []
                for i in range(len(patient_list)):
                    p_record = Record.select().join(Appointment).where(Appointment.patient_id == patient_list[i])
                    if p_record:                        
                        for r in p_record:
                            appointment = Appointment.get_or_none(Appointment.id == r.appointment_id)                            
                            my_patient_record.append(                                
                                {
                                    "record_id": r.id,
                                    "appointment_id": r.appointment_id,
                                    "report": r.report,
                                    "prescription": r.prescription,
                                    "payment_amount": str(r.payment_amount),
                                    "paid": r.paid,
                                    "cholestrol_level": str(r.cholestrol_level),
                                    "sugar_level": str(r.sugar_level),
                                    "systolic_blood_pressure": r.systolic_blood_pressure,
                                    "diastolic_blood_pressure": r.diastolic_blood_pressure,
                                    "doctor_id" : appointment.doctor_id,
                                    "patient_id" : appointment.patient_id   
                                }                      
                            )
                        response = {
                            "my_patient_record": my_patient_record,
                            "message": "successfully retrieve record!",
                            "status": "success"
                        }
                    else:
                        response["my_patient_record"] = []
        else:
            response = {
            "message": "Record not found",
            "status": "failed"
            }
    else:
        response = {
            "message": "Record not found",
            "status": "failed"
        }
    return jsonify(response)

@records_api_blueprint.route('/me', methods=['GET'])
@jwt_required
def me():
    online_user = get_jwt_identity()
    user = User.get_or_none(User.id == online_user['id'])

    if user:
        role_list = Role.select().join(UserRole).where(UserRole.user_id == user.id) #select all existing role(s)
        role_name_list = []
        for r in role_list:
            role_name_list.append(r.role_name)
        if ("patient" in role_name_list) and ("guardian" in role_name_list):
            response={
                        "message": "successfully retrieve record!",
                        "status": "success"
                    }
            #my patient's record
            p_list = User.select().where(User.guardian_id==user.id)
            if p_list:
                patient_list = []
                for p in p_list:
                    patient_list.append(p.id)
                my_patient_record = []
                for i in range(len(patient_list)):
                    p_record = Record.select().join(Appointment).where(Appointment.patient_id == patient_list[i])
                    if p_record:
                        for r in p_record:
                            appointment = Appointment.get_or_none(Appointment.id == r.appointment_id)
                            my_patient_record.append({
                                    "record_id": r.id,
                                    "appointment_id": r.appointment_id,
                                    "report": r.report,
                                    "prescription": r.prescription,
                                    "payment_amount": str(r.payment_amount),
                                    "paid": r.paid,
                                    "cholestrol_level": str(r.cholestrol_level),
                                    "sugar_level": str(r.sugar_level),
                                    "systolic_blood_pressure": r.systolic_blood_pressure,
                                    "diastolic_blood_pressure": r.diastolic_blood_pressure,
                                    "doctor_id" : appointment.doctor_id,
                                    "patient_id" : appointment.patient_id                                    
                                    }
                            )
                        response["my_patient_record"] = my_patient_record
                    else:
                        response["my_patient_record"] = []
            #My own record
            record_list = Record.select().join(Appointment).where(Appointment.patient_id == user.id)
            guardian_record = []
            if record_list:
                for r in record_list:
                    appointment = Appointment.get_or_none(Appointment.id == r.appointment_id)
                    guardian_record.append({
                            "record_id": r.id,
                            "appointment_id": r.appointment_id,
                            "report": r.report,
                            "prescription": r.prescription,
                            "payment_amount": str(r.payment_amount),
                            "paid": r.paid,
                            "cholestrol_level": str(r.cholestrol_level),
                            "sugar_level": str(r.sugar_level),
                            "systolic_blood_pressure": r.systolic_blood_pressure,
                            "diastolic_blood_pressure": r.diastolic_blood_pressure,
                            "doctor_id" : appointment.doctor_id,
                            "patient_id" : appointment.patient_id                            
                        }
                    )
                    
                response["guardian_record"] = guardian_record 
                print(response)
            else:
                response["guardian_record"] = []     
        elif "patient" in role_name_list:
            record_list = Record.select().join(Appointment).where(Appointment.patient_id == user.id)
            my_patient_record = []
            if record_list:
                for r in record_list:
                    appointment = Appointment.get_or_none(Appointment.id == r.appointment_id)
                    my_patient_record.append({
                            "record_id": r.id,
                            "appointment_id": r.appointment_id,
                            "report": r.report,
                            "prescription": r.prescription,
                            "payment_amount": str(r.payment_amount),
                            "paid": r.paid,
                            "cholestrol_level": str(r.cholestrol_level),
                            "sugar_level": str(r.sugar_level),
                            "systolic_blood_pressure": r.systolic_blood_pressure,
                            "diastolic_blood_pressure": r.diastolic_blood_pressure,
                            "doctor_id" : appointment.doctor_id,
                            "patient_id" : appointment.patient_id
                        }                        
                    )
                response = {
                            "my_patient_record": my_patient_record,
                            "message": "successfully retrieve record!",
                            "status": "success"
                        }
            else:
                response["patient_record"] = []
        elif "doctor" in role_name_list:
            record_list = Record.select().join(Appointment).where(Appointment.doctor_id == user.id)
            doctor_record = []
            if record_list:
                for r in record_list:
                    appointment = Appointment.get_or_none(Appointment.id == r.appointment_id)
                    doctor_record.append({
                            "record_id": r.id,
                            "appointment_id": r.appointment_id,
                            "report": r.report,
                            "prescription": r.prescription,
                            "payment_amount": str(r.payment_amount),
                            "paid": r.paid,
                            "cholestrol_level": str(r.cholestrol_level),
                            "sugar_level": str(r.sugar_level),
                            "systolic_blood_pressure": r.systolic_blood_pressure,
                            "diastolic_blood_pressure": r.diastolic_blood_pressure,
                            "doctor_id" : appointment.doctor_id,
                            "patient_id" : appointment.patient_id                            
                        }
                    )
                response = {
                            "doctor_record": doctor_record,
                            "message": "successfully retrieve record!",
                            "status": "success"
                        }
            else:
                response["doctor_record"] = [] 
        elif "guardian" in role_name_list:
            #my patient's record
            p_list = User.select().where(User.guardian_id==user.id)
            if p_list:
                patient_list = []
                for p in p_list:
                    patient_list.append(p.id)
                my_patient_record = []
                for i in range(len(patient_list)):
                    p_record = Record.select().join(Appointment).where(Appointment.patient_id == patient_list[i])
                    if p_record:                        
                        for r in p_record:
                            appointment = Appointment.get_or_none(Appointment.id == r.appointment_id)                            
                            my_patient_record.append(                                
                                {
                                    "record_id": r.id,
                                    "appointment_id": r.appointment_id,
                                    "report": r.report,
                                    "prescription": r.prescription,
                                    "payment_amount": str(r.payment_amount),
                                    "paid": r.paid,
                                    "cholestrol_level": str(r.cholestrol_level),
                                    "sugar_level": str(r.sugar_level),
                                    "systolic_blood_pressure": r.systolic_blood_pressure,
                                    "diastolic_blood_pressure": r.diastolic_blood_pressure,
                                    "doctor_id" : appointment.doctor_id,
                                    "patient_id" : appointment.patient_id   
                                }                      
                            )
                        response = {
                            "my_patient_record": my_patient_record,
                            "message": "successfully retrieve record!",
                            "status": "success"
                        }
                    else:
                        response["my_patient_record"] = []
        else:
            response = {
            "message": "Record not found",
            "status": "failed"
            }
    else:
        response = {
            "message": "Record not found",
            "status": "failed"
        }
    return jsonify(response)

@records_api_blueprint.route('/', methods=['GET'])
@jwt_required
def search():
    id = request.json.get("record_id")
    record = Record.get_or_none(Record.id==id)
    appointment = Appointment.get_or_none(Appointment.id==record.appointment_id)
    if record:
        return jsonify({
            "record_id": record.id,
            "appointment_id": record.appointment_id,
            "report": record.report,
            "prescription": record.prescription,
            "payment_amount": str(record.payment_amount),
            "paid": record.paid,
            "cholestrol_level": str(record.cholestrol_level),
            "sugar_level": str(record.sugar_level),
            "systolic_blood_pressure": record.systolic_blood_pressure,
            "diastolic_blood_pressure": record.diastolic_blood_pressure,
            "doctor_id" : appointment.doctor_id,
            "patient_id" : appointment.patient_id  
        })
    else:
        return jsonify({
            "message": "There is no such appointment.",
            "status": "failed"
            })

@records_api_blueprint.route('/update', methods=['POST'])
@jwt_required
def update():
    online_user = get_jwt_identity()
    user = User.get_or_none(User.id == online_user['id'])

    if user:
        role_list = Role.select().join(UserRole).where(UserRole.user_id == user.id) #select all existing role(s)
        role_name_list = []
        for r in role_list:
            role_name_list.append(r.role_name)
        if ("doctor" in role_name_list):
            record_id = request.json.get("record_id")
            update_record = Record.get_or_none(Record.id == record_id)
            if update_record:
                update_record.report = request.json.get("report")
                update_record.prescription = request.json.get("prescription")
                update_record.payment_amount = request.json.get("payment_amount")
                if update_record.save():
                    response = {
                        "message": "Updated record successfully",
                        "status": "success",
                        "report": update_record.report
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
