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
    params = request.json
    doctor_ic = params.get("doctor_ic")
    patient_ic = params.get("patient_ic")
    start_datetime = params.get("start_datetime")
    end_datetime = params.get("end_datetime")

    doctor = User.get_or_none(User.ic_number==doctor_ic)
    patient = User.get_or_none(User.ic_number==patient_ic)
    if doctor and patient:
        new_appointment = Appointment(doctor_id=doctor.id, patient_id=patient.id, start_datetime=start_datetime, end_datetime=end_datetime)
        if new_appointment.save():
            return jsonify({
                "message": "Successfully created an appointment",
                "status ": "success",
                "doctor_id": new_appointment.doctor_id,
                "patient_id": new_appointment.patient_id,
                "start_datetime": new_appointment.start_datetime,
                "end_datetime": new_appointment.end_datetime
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
    else:
        return jsonify({
            "message": "Can't find doctor or patient",
            "status ": "fail",
        })

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
                        "start_time": a.start_datetime,
                        "end_time": a.end_datetime
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
                                "start_time": a.start_datetime,
                                "end_time": a.end_datetime,
                            })
                            else:
                                response["message"] = "Successfully retrieve appointment!"
                                guardian_record.append({
                                "appointment_id": a.id,
                                "doctor_id": a.doctor_id,
                                "patient_id": a.patient_id,
                                "start_time": a.start_datetime,
                                "end_time": a.end_datetime,
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
                        "start_time": a.start_datetime,
                        "end_time": a.end_datetime
                    })
                response["patient_record"] = patient_record
                return jsonify(response)
            else:
                return jsonify({
                    "message": "This patient has no upcoming appointment.",
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
                            "start_time": a.start_datetime,
                            "end_time": a.end_datetime
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
    ic_number = request.args.get("ic_number")
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
                    "start_time": a.start_datetime,
                    "end_time": a.end_datetime,
                })
                
                if enddatetime > current_date_time:
                    response["message"] = "Successfully retrieve appointment!"
                    upcoming_list.append({
                    "appointment_id": a.id,
                    "doctor_id": a.doctor_id,
                    "patient_id": a.patient_id,
                    "start_time": a.start_datetime,
                    "end_time": a.end_datetime
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

@appointments_api_blueprint.route('/search', methods=['GET'])
@jwt_required
def search():
    id = request.args.get("appointment_id")
    appointment = Appointment.get_or_none(Appointment.id==id)
    record = Record.get_or_none(Record.appointment_id == id)
    doctor = User.get_or_none(User.id == appointment.doctor_id)
    patient = User.get_or_none(User.id == appointment.patient_id)
    
    if record:
        if record.zoom_url:
            zoom_link = record.zoom_url
        else:
            zoom_link = ""
    else:
        pass

    if appointment:
        return jsonify({
            "appointment_id": appointment.id,
            "doctor_id": appointment.doctor_id,
            "patient_id": appointment.patient_id,
            "doctor_ic": doctor.ic_number,
            "patient_ic": patient.ic_number,
            "doctor_name": doctor.name,
            "patient_name": patient.name,
            "appointment_start": appointment.start_datetime,
            "appointment_end": appointment.end_datetime,
            "zoom_link": zoom_link
        })
    else:
        return jsonify({
            "message": "There is no such appointment.",
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

@appointments_api_blueprint.route('/create_client', methods=['GET'])
@jwt_required
def create_client():
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
    record = Record.get_or_none(Record.appointment_id == id)

    record.zoom_url = join_url
    if record.save():
        return join_url
    else:
        return "fail"



# @appointments_api_blueprint.route('/create_signature', methods=['POST'])
# @jwt_required
# def create_signature():
#     import hashlib
#     import hmac
#     import base64
#     import time
#     from app import app

#     ts = int(round(time.time() * 1000)) - 30000
#     msg = app.config.get('ZOOM_API_KEY') + str(request.json.get('meetingNumber')) + str(ts) + str(request.json.get('role'));   
#     message = base64.b64encode(bytes(msg, 'utf-8'))
#     # message = message.decode("utf-8");    
#     secret = bytes(app.config.get('ZOOM_API_SECRET'), 'utf-8')
#     hash = hmac.new(secret, message, hashlib.sha256)
#     hash =  base64.b64encode(hash.digest())
#     hash = hash.decode("utf-8")
#     tmpString = "%s.%s.%s.%s.%s" % (app.config.get('ZOOM_API_KEY'), str(request.json.get('meetingNumber')), str(ts), str(request.json.get('role')), hash)
#     signature = base64.b64encode(bytes(tmpString, "utf-8"))
#     signature = signature.decode("utf-8")
#     return signature.rstrip("=")




# @appointments_api_blueprint.route('/create_room', methods=['POST'])
# @jwt_required
# def create_room():
#     from twilio.rest import Client
#     from app import app
#     appointment_id = request.json.get('appointment_id')
#     account_sid = app.config.get('TWILIO_SID')
#     auth_token = app.config.get('TWILIO_AUTHTOKEN')
#     client = Client(account_sid, auth_token)

#     #create peer to peer room ==> https://www.twilio.com/docs/video/api/rooms-resource#post-list-resource
#     room = client.video.rooms.create(
#                                 enable_turn=True,
#                                 status_callback='http://127.0.0.1:5000/api/v1/appointments/roomevent',
#                                 type='peer-to-peer',
#                                 unique_name=f'test20'
#                             )
#     response={
#         "room_sid": room.sid,
#         "message": "created room",

#     }
#     return jsonify(response)
    
# @appointments_api_blueprint.route('/create_access', methods=['GET'])
# @jwt_required
# def create_access():
#     from twilio.jwt.access_token import AccessToken
#     from twilio.jwt.access_token.grants import VideoGrant
#     from app import app
#     # Required for all Twilio Access Tokens
#     account_sid = app.config.get('TWILIO_SID')
#     api_key = app.config.get('TWILIO_API_KEY')
#     api_secret = app.config.get('TWILIO_API_SECRET')

#     # required for Video grant
#     online_user = get_jwt_identity()
#     identity = online_user['name'] + " (" + online_user['ic_number'] + ")"

#     # Create Access Token with credentials
#     token = AccessToken(account_sid, api_key, api_secret, identity=identity)

#     # Create a Video grant and add to token
#     online_user = get_jwt_identity()
#     user = User.get_or_none(User.id == online_user['id'])
#     video_grant = VideoGrant(room=f'remotemed appointment')
#     token.add_grant(video_grant)

#     # Return token info as JSON
#     print(token.to_jwt())

#     return token.to_jwt()

# @appointments_api_blueprint.route('/roomevent', methods=['POST'])
# def roomevent():
#     status = request.json.get('StatusCallbackEvent')
#     timestamp = request.json.get('Timestamp')

#     response = {
#         "status": status,
#         "timestamp": timestamp 
#     }
#     print(response)
#     return jsonify(response)