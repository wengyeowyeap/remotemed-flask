from flask import Blueprint, request, jsonify
from models.record import Record
from models.appointment import Appointment
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.user import User
from models.record import Record
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
            response = {
                "message": "Add record failed, please try again",
                "status": "failed"
            } 
            #Image Upload Start
        for i in range(int(request.form.get('image_count'))):
            image = request.files['image_files'+ str(i)]
            caption = request.form.get('caption'+ str(i))

            if 'image' not in image.mimetype:
                patient_record.delete_instance()
                response = {
                    "message": "One or more of the uploaded files is not an image. Please try again",
                    "status": "failed"
                }
                return jsonify(response)
            else:
                file_extension = image.mimetype 
                file_extension = file_extension.replace('image/', '.')
                image.filename = str(datetime.now()) + file_extension
                image.filename = secure_filename(image.filename)
                image_url = upload_file_to_s3(image, user.ic_number)
                upload_image = Patient_Photo(record_id = 1, image_url = image_url, caption = caption)
                
                if upload_image.save():
                    good_response["image"+str(i+1)] = {
                                                        "image_url" : upload_image.full_image_url,
                                                        "caption" : caption
                                                    }
                    response = good_response
                else:
                    patient_record.delete_instance()
                    response = {
                        "message": "Image upload failed, please try again",
                        "status": "failed"
                    }
    else:
        response = {
                        "message": "Image upload failed, please try again",
                        "status": "failed"
                    } 
    return jsonify(response)


