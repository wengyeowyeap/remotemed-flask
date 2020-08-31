from flask import Blueprint, jsonify, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.user import User
from models.user_disease import UserDisease
from models.user_role import UserRole
from models.disease import Disease
from models.role import Role
from werkzeug.security import check_password_hash

users_api_blueprint = Blueprint('users_api',
                             __name__,
                             template_folder='templates')

@users_api_blueprint.route('/create', methods=['POST'])
@jwt_required
def create():
    name = request.json.get('name')
    password = request.json.get('password')
    email = request.json.get('email')
    ic_number = request.json.get('ic_number')
    gender = request.json.get('gender')
    role = request.json.get('role')

    if ("1" in role) or ("1" in role and "2" in role) : #if this is patient or patient/guardian
        new_guardian = User.get_or_none(User.ic_number == request.json.get('guardian'))
        disease = request.json.get('disease') #value need to be number, example: 1->diabetes
        new_user = User(name = name, password = password, email = email, ic_number = ic_number, gender = gender, guardian = new_guardian.id)   
        if new_user.save():
            for i in range(len(disease)):
                user_disease = UserDisease(disease=int(disease[i-1]), user=new_user)
                if user_disease.save():
                    pass
                else:
                    response = {
                        "message": "Some error occured, please try again",
                        "status": "failed"
                    }
            if "1" in role and "2" in role:
                user_role = UserRole(role=1, user=new_user)
                user_role2 = UserRole(role=2, user=new_user)
                if user_role.save() and user_role2.save():
                    disease_name_list = []
                    disease_list = Disease.select().join(UserDisease).where(UserDisease.user_id == new_user.id)
                    for d in disease_list:
                        disease_name_list.append(d.disease_name)
                    response = {
                        "message": f"Successfully created a user.",
                        "status": "success",
                        "user": {
                            "id": new_user.id,
                            "name": new_user.name,
                            "email": new_user.email,
                            "ic_number": new_user.ic_number,
                            "gender": new_user.gender,
                            "role": [user_role.role.role_name, user_role2.role.role_name],
                            "guardian": new_user.guardian.id
                        }
                    }
                    response["user"]["disease"] = disease_name_list
                else:
                    response = {
                        "message": "Some error occured, please try again",
                        "status": "failed"
                    }
            else:
                user_role = UserRole(role=1, user=new_user)
                if user_role.save():
                    disease_name_list = []
                    disease_list = Disease.select().join(UserDisease).where(UserDisease.user_id == new_user.id)
                    for d in disease_list:
                        disease_name_list.append(d.disease_name)
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
                            "guardian": new_user.guardian.id
                        }
                    }
                    response["user"]["disease"] = disease_name_list
                else:
                    response = {
                        "message": "Some error occured, please try again",
                        "status": "failed"
                    }
                
        else:
            error_message = []
            for error in new_user.errors:
                error_message.append(error)
            response = {
                        "message": error_message,
                        "status": "failed"
            }   
    else: # not patient
        new_user = User(name = name, password = password, email = email, ic_number = ic_number, gender = gender, guardian = None)
        if new_user.save():  
            user_role = UserRole(role=int(role[0]), user=new_user)     
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
                    }
                }
            else:
                response = {
                    "message": "Some error occured, please try again",
                    "status": "failed"
                }
        else:
            error_message = []
            for error in new_user.errors:
                error_message.append(error)
            response = {
                        "message": error_message,
                        "status": "failed"
            }                         
    return jsonify(response)

@users_api_blueprint.route('/edit', methods=['POST'])
@jwt_required
def edit():
    ic_number = request.json.get('ic_number')
    user = User.get_or_none(User.ic_number == ic_number)
    online_user = get_jwt_identity()
    if user:
        #change item in User table
        user.name = request.json.get('name')
        user.password = request.json.get('password')
        user.email = request.json.get('email')
        user.gender = request.json.get('gender')

        if request.json.get('guardian'):
            new_guardian = User.get_or_none(User.ic_number == request.json.get('guardian'))
            user.guardian = new_guardian.id
        else:
            pass


        role = request.json.get('role')
        disease = request.json.get('disease')

        if user.save():
            if user.id != online_user['id']:
                
                role_list = UserRole.select().where(UserRole.user_id == user.id) #select all existing role(s)
                #Delete obselete role
                for r in role_list:
                    if r not in role:
                        del_role = UserRole.get_or_none(UserRole.role_id == r.role_id, UserRole.user_id == user.id)
                        del_role.delete_instance()
                #Add new role
                for i in range(len(role)):
                    if role[i-1] not in role_list:
                        new_role = UserRole(user = user, role_id = role[i-1])
                        if new_role.save():
                            pass
                        else:
                            response = {
                                    "message": "Can't add new role, please try again",
                                    "status": "failed"
                                }
                if "1" in role:
                    disease_list = UserDisease.select().where(UserDisease.user_id == user.id) #select all existing disease(s)
                    #Add new disease
                    for d in disease_list:
                        if d not in disease:
                            del_disease = UserDisease.get_or_none(UserDisease.disease_id == d.disease_id, UserDisease.user_id == user.id)
                            del_disease.delete_instance()                        
                    #delete obsolete disease
                    for i in range(len(disease)):
                        if disease[i-1] not in disease_list:
                            new_disease = UserDisease(user = user, disease_id = disease[i-1])
                            if new_disease.save():
                                pass
                        else:
                            response = {
                                    "message": "Can't add new disease, please try again",
                                    "status": "failed"
                                }
                response = {
                    "message": "Updated user info successfully!",
                    "status": "success"
                }
            else:
                response = {
                    "message": "Updated user info successfully!",
                    "status": "success"
                }
        else:
            response = {
                    "message": "Cant save user, please try again",
                    "status": "failed"
                }
    else:
        response = {
                    "message": "Cant save user, please try again",
                    "status": "failed"
                }
    return jsonify(response)

@users_api_blueprint.route('/check_ic', methods=['GET'])
def check_ic():
    input = request.args.get("ic")
    find_user = User.get_or_none(User.ic_number == input)
    if find_user:
        response = {
            "exists": True,
            "valid": False
        }
    else:
        response = {
            "exists": False,
            "valid": True
        }
    return jsonify(response)

@users_api_blueprint.route('/check_email', methods=['GET'])
def check_email():
    input = request.args.get("email")
    find_email = User.get_or_none(User.email == input)
    if find_email:
        response = {
            "exists": True,
            "valid": False
        }
    else:
        response = {
            "exists": False,
            "valid": True
        }
    return jsonify(response)

@users_api_blueprint.route('/check_guardian', methods=['GET'])
def check_guardian():
    input = request.args.get("guardian_id")
    #guardian req: role = patient or guardian
    user = User.get_or_none(User.ic_number == input)
    if user:
        role_list = UserRole.select().where(UserRole.user_id == user.id) #select all existing role(s)
        role_id_list = []
        for r in role_list:
            role_id_list.append(r.role_id)
        if 1 in role_id_list or 2 in role_id_list :
            response = {
                "valid": True,
                "name": user.name
            }
        else:
            response = {
                "valid": False,
                "message": "User does not qualify to be a guardian"
            }
    else:
        response = {
                "valid": False,
                "message": "User not exist"
            }
    return jsonify(response)

@users_api_blueprint.route('/check_doctor', methods=['GET'])
def check_doctor():
    input = request.args.get("doctor_ic")
    doctor = User.get_or_none(User.ic_number == input)
    if doctor:
        role_list = UserRole.select().where(UserRole.user_id == doctor.id)
        role_id_list = []
        for r in role_list:
            role_id_list.append(r.role_id)
        if 3 in role_id_list:
            response = {
                "is_doctor": True,
                "name": doctor.name
            }
        else:
            response = {
                "is_doctor": False
            }
    else:
        response = {
            "valid": False,
            "message": "User not exist"
        }
    return jsonify(response)

@users_api_blueprint.route('/check_patient', methods=['GET'])
def check_patient():
    input = request.args.get("patient_ic")
    patient = User.get_or_none(User.ic_number == input)
    if patient:
        role_list = UserRole.select().where(UserRole.user_id == patient.id)
        role_id_list = []
        for r in role_list:
            role_id_list.append(r.role_id)
        if 1 in role_id_list:
            response = {
                "is_patient": True,
                "name": patient.name
            }
        else:
            response = {
                "is_patient": False
            }
    else:
        response = {
            "valid": False,
            "message": "User not exist"
        }
    return jsonify(response)

@users_api_blueprint.route('/show_patient', methods=['GET'])
@jwt_required
def show_patient():
    user_ic = request.args.get("ic_number")
    user = User.get_or_none(User.ic_number == user_ic)

    if user:
        role_list = Role.select().join(UserRole).where(UserRole.user_id == user.id) #select all existing role(s)
        role_name_list = []
        for r in role_list:
            role_name_list.append(r.role_name)
        if "patient" in role_name_list:
            disease_list = Disease.select().join(UserDisease).where(UserDisease.user_id == user.id) #select all existing disease(s)
            disease_name_list = []
            for d in disease_list:
                disease_name_list.append(d.disease_name)
            if user.guardian.name:
                display_guardian = user.guardian.name
            else:
                display_guardian = None
            response = {
                            "id": user.id,
                            "name": user.name,
                            "email": user.email,
                            "ic_number": user.ic_number,
                            "gender": user.gender,
                            "role": role_name_list,
                            "disease": disease_name_list,
                            "guardian": display_guardian
                        }
        
        else:
            response = {
            "message": "Patient not found",
            "status": "failed"
        }
    else:
        response = {
            "message": "Patient not found",
            "status": "failed"
        }
    return jsonify(response)

@users_api_blueprint.route('/show_my_patient', methods=['GET'])
@jwt_required
def show_my_patient():
    online_user = get_jwt_identity()
    guardian = User.get_or_none(User.id == online_user['id'])

    if guardian:
        role_list = UserRole.select().where(UserRole.user_id == guardian.id)
        role_id_list = []
        for r in role_list:
            role_id_list.append(r.role_id)
        if 2 in role_id_list:
            patient_list = User.select().where(User.guardian_id == guardian.id)
            if patient_list:
                my_patient = []
                for p in patient_list:
                    disease_list = Disease.select().join(UserDisease).where(UserDisease.user_id == p.id) #select all existing disease(s)
                    disease_name_list = []
                    for d in disease_list:
                        disease_name_list.append(d.disease_name)
                    my_patient.append(
                        {
                            "id": p.id,
                            "name": p.name,
                            "email": p.email,
                            "ic_number": p.ic_number,
                            "gender": p.gender,
                            "disease": disease_name_list,
                        }
                    )
                response = {
                    "status": "success",
                    "is_guardian": True,
                    "my_patient": my_patient
                }
            else:
                response = {
                    "message": "This guardian has no patient",
                    "is_guardian": True,
                    "status": "fail"
                }

        else:
            response = {
                "is_guardian": False,
                "status": "fail"
            }
    else:
        response = {
            "valid": False,
            "message": "User not exist",
            "status": "fail"
        }
    return jsonify(response)

@users_api_blueprint.route('/me', methods=['GET'])
@jwt_required
def me():
    online_user = get_jwt_identity()
    user = User.get_or_none(User.id == online_user['id'])
 
    if user:
    
        response = {
                        "id": user.id,
                        "name": user.name,
                        "email": user.email,
                        "ic_number": user.ic_number,
                        "gender": user.gender,
                    }

    else:
        response = {
            "message": "User not found",
            "status": "failed"
        }
    return jsonify(response)
