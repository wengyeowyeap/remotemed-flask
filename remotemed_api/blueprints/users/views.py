from flask import Blueprint, jsonify, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.user import User
from models.user_disease import UserDisease
from models.user_role import UserRole
from werkzeug.security import check_password_hash

users_api_blueprint = Blueprint('users_api',
                             __name__,
                             template_folder='templates')

@users_api_blueprint.route('/sign_up', methods=['POST'])
def sign_up():
    name = request.json.get('name')
    password = request.json.get('password')
    email = request.json.get('email')
    ic_number = request.json.get('ic_number')
    gender = request.json.get('gender')
    role = request.json.get('role')

    if role == "1" or role == "1, 2": #if this is patient or patient/guardian
        guardian = request.json.get('guardian')
        disease = request.json.get('disease') #value need to be number, example: 1->diabetes
        new_user = User(name = name, password = password, email = email, ic_number = ic_number, gender = gender, guardian = guardian)   
        user_disease = UserDisease(disease=disease, user=new_user)
        if new_user.save() and user_disease.save():
            if role == "1":
                user_role = UserRole(role=int(role), user=new_user)
                if user_role.save():
                    response = {
                        "message": f"Successfully created a user.",
                        "status": "success",
                        "user": {
                            "id": new_user.id,
                            "name": new_user.name,
                            "email": new_user.email,
                            "ic_number": new_user.ic_number,
                            "gender": new_user.gender,
                            "role": user_role.role.role_name,
                            "disease": user_disease.disease.disease_name,
                            "guardian": new_user.guardian
                        }
                    }
                else:
                    response = {
                        "message": "Some error occured, please try again",
                        "status": "failed"
                    }
            else:
                user_role = UserRole(role=1, user=new_user)
                user_role2 = UserRole(role=2, user=new_user)
                if user_role.save() and user_role2.save():
                    response = {
                        "message": f"Successfully created a user.",
                        "status": "success",
                        "user": {
                            "id": new_user.id,
                            "name": new_user.name,
                            "email": new_user.email,
                            "ic_number": new_user.ic_number,
                            "gender": new_user.gender,
                            "role": user_role.role,
                            "role2": user_role2.role,
                            "disease": user_disease.disease,
                            "guardian": new_user.guardian
                        }
                    }
                else:
                    response = {
                        "message": "Some error occured, please try again",
                        "status": "failed"
                    }
        else:
            error_message = ""
            for error in new_user.errors:
                error_message = error_message + error + ", "
            response = {
                        "message": f"{error_message}",
                        "status": "failed"
            }
    else: # not patient
        new_user = User(name = name, password_hash = password, email = email, ic_number = ic_number, gender = gender, guardian = None)
        if new_user.save():   
            user_role = UserRole(role=int(role), user=new_user)     
            if user_role.save():
                response = {
                    "message": f"Successfully created a user.",
                    "status": "success",
                    "user": {
                        "id": new_user.id,
                        "name": new_user.name,
                        "email": new_user.email,
                        "ic_number": new_user.ic_number,
                        "gender": new_user.gender,
                        "role": user_role.role,
                    }
                }
            else:
                response = {
                    "message": "Some error occured, please try again",
                    "status": "failed"
                }
        else:
            error_message = ""
            for error in new_user.errors:
                error_message = error_message + error + ", "
            response = {
                        "message": f"{error_message}",
                        "status": "failed"
            }                         
    return jsonify(response)


