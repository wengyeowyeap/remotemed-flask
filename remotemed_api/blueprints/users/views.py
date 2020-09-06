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
def create():
    name = request.json.get('name')
    password = request.json.get('password')
    email = request.json.get('email')
    ic_number = request.json.get('ic_number')
    gender = request.json.get('gender')
    role = request.json.get('role')
    disease = request.json.get('disease')

    if (("1" in role) or ("2" in role)) and (("3" in role) or ("4" in role)):
        response = {
            "message": "Patient/Guardian cannot be Doctor/Admin at the same time.",
            "status": "fail"
        }
    else:
        if ("1" in role) or (("1" in role) and ("2" in role)):  # if this is patient or patient/guardian
            guardian = request.json.get('guardian')
            if guardian: #If there is guardian entered
                new_guardian = User.get_or_none(User.ic_number == request.json.get('guardian'))
                guardian_id = new_guardian
            else:
                guardian_id = None
            if disease: #If there is disease entered
                pass
            else: #If there is no disease entered for a patient, return error
                return jsonify({
                    "message": "Did not enter disease for patient.",
                    "status": "fail"
                })
            new_user = User(name=name, password=password, email=email, ic_number=ic_number, gender=gender, guardian=guardian_id)
            if new_user.save():
                #handle disease for both patient and patient/guardian
                for i in range(len(disease)):
                    new_user_disease = UserDisease(disease=int(disease[i-1]), user=new_user)
                    if new_user_disease.save():
                        pass
                    else:
                        response = new_user.error() #method from models.user
                if "1" in role and "2" in role:
                    #handle role for patient/guardian
                    user_role = UserRole(role=role[0], user=new_user)
                    user_role2 = UserRole(role=role[1], user=new_user)
                    if user_role.save() and user_role2.save():
                        #response after saved user, disease, role
                        response = {
                            "message": f"Successfully created a user.",
                            "status": "success",
                            "user": {
                                "id": new_user.id,
                                "name": new_user.name,
                                "email": new_user.email,
                                "ic_number": new_user.ic_number,
                                "gender": new_user.gender,
                                "role": new_user.role, #hybrid property
                                "disease": new_user.disease #hybrid property
                            }
                        }
                        if new_user.guardian: #append guardian if there is one, else append as none
                            response['user']['guardian'] = new_user.guardian.name                        
                        else:
                            response['user']['guardian'] = None
                    else:
                        response = new_user.error() #method from models.user
                else:
                    #handle role for patient
                    user_role = UserRole(role=role[0], user=new_user)
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
                                "role": new_user.role, #hybrid property
                                "disease": new_user.disease #hybrid property
                            }
                        }
                        if new_user.guardian: #append guardian if there is one, else append as none
                            response['user']['guardian'] = new_user.guardian.name                        
                        else:
                            response['user']['guardian'] = None
                    else:
                        response = new_user.error() #method from models.user
            else:
                response = new_user.error() #method from models.user
        else:  # doctor or admin
            if ("3" in role) and ("4" in role):
                response = {
                    "message": "A user cannot be a Doctor and Admin at the same time",
                    "status": "fail"
                }
            else:
                new_user = User(name=name, password=password, email=email,ic_number=ic_number, gender=gender, guardian=None)
                if new_user.save():
                    user_role = UserRole(role=role[0], user=new_user)
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
                                "role": new_user.role, #hybrid property
                            }
                        }
                    else:
                        response = new_user.error() #method from models.user
                else:
                   response = new_user.error() #method from models.user
    return jsonify(response)


@users_api_blueprint.route('/edit_by_admin', methods=['POST']) #edit name, pw, email, gender, role, disease, guardian
@jwt_required
def edit_by_admin():
    ic_number = request.json.get('ic_number')
    user = User.get_or_none(User.ic_number == ic_number) #user to be edited
    online_user = get_jwt_identity() 
    current_user = User.get_or_none(User.id == online_user['id']) #user that is editing
    
    if user: #check existence of user
        if ("admin" in current_user.role): #check editing user is admin (if not, 401)
            #set attributes that is 'sure have'
            user.name = request.json.get('name')
            user.password = request.json.get('password')
            user.email = request.json.get('email')
            user.gender = request.json.get('gender')

            #handle guardian
            if request.json.get('guardian'): #if guardian is inputted
                new_guardian = User.get_or_none(User.ic_number == request.json.get('guardian'))
                user.guardian = new_guardian.id #update/remain according to input
            else: #if no guardian is inputted, delete the guardian
                user.guardian = None 
            
            if user.save(): # save the fields in user table first
                #handle role
                role = request.json.get('role')
                if role: #if role is inputted
                    if (("1" in role) or ("2" in role)) and (("3" in role) or ("4" in role)):
                        return jsonify({
                            "message": "Patient/Guardian cannot be Doctor/Admin at the same time.",
                            "status": "fail"
                        })
                    elif ("3" in role) and ("4" in role):
                        return jsonify({
                            "message": "A user cannot be a Doctor and Admin at the same time",
                            "status": "fail"
                        })
                    elif (("1" in user.role_id) or ("2" in user.role_id)) and (("3" in role) or ("4" in role)):
                        return jsonify({
                            "message": "A user cannot switch role from Patient/Guardian to Doctor/Admin",
                            "status": "fail"
                        })
                    elif (("3" in user.role_id) or ("4" in user.role_id)) and (("1" in role) or ("2" in role)):
                        return jsonify({
                            "message": "A user cannot switch role from Doctor/Admin to Patient/Guardian",
                            "status": "fail"
                        })
                    else:
                        if sorted(user.role_id) == sorted(role): #if same, no need change
                            pass
                        else:
                            # Delete obselete role
                            role_to_delete = []
                            for i in range(len(user.role_id)):
                                if user.role_id[i] not in role:
                                    role_to_delete.append(user.role_id[i])
                            for i in range(len(role_to_delete)):
                                del_role = UserRole.get_or_none(UserRole.role == role_to_delete[i], UserRole.user == user)
                                del_role.delete_instance()
                            # Add new role
                            for i in range(0,len(role)):
                                if role[i] not in user.role_id:
                                    new_role = UserRole(user=user, role=role[i])
                                    if new_role.save():
                                        pass
                                    else:
                                        return jsonify({
                                            "message": "Problem occured when saving new role.",
                                            "status": "fail"
                                        })
                else: #if no role is inputted, remain
                    pass #Note: If can prefill role in frontend, should change to warning message "user cannot have no role"
                if "1" in user.role_id: #after saving new role(s), this checks the updated version of the user's role(s)
                    #handle disease
                    disease = request.json.get('disease')
                    if disease:
                        if sorted(user.disease_id) == sorted(disease): #if same, no need change
                            pass
                        else:
                            # Delete obselete disease
                            disease_to_delete = []
                            for i in range(len(user.disease_id)):
                                if user.disease_id[i] not in disease:
                                    disease_to_delete.append(user.disease_id[i])
                            for i in range(len(disease_to_delete)):
                                del_disease = UserDisease.get_or_none(UserDisease.disease == disease_to_delete[i], UserDisease.user == user)
                                del_disease.delete_instance()
                            # Add new disease
                            for i in range(len(disease)):
                                if disease[i] not in user.disease_id:
                                    new_disease = UserDisease(user=user, disease=disease[i])
                                    if new_disease.save():
                                        pass
                                    else:
                                        return jsonify({
                                            "message": "Problem occured when saving new disease.",
                                            "status": "fail"
                                        })
                    else: #if no disease is inputted, remain
                        pass #Note: If can prefill disease in frontend, should change to warning message "patient cannot have no disease"
                response = {
                    "message": "Successfully edited user.",
                    "status": "success"
                }
            else:
                response = user.error()
        else:
            response = {
                "message": "401 Unauthorized",
                "status": "fail"
            }
    else:
        response = {
            "message": "User not found, please try again",
            "status": "fail"
        }
    return jsonify(response)

@users_api_blueprint.route('/edit_by_me_or_guardian', methods=['POST']) #ONLY edit name, pw, email, gender
@jwt_required
def edit_by_me_or_guardian():
    ic_number = request.json.get('ic_number')
    user = User.get_or_none(User.ic_number == ic_number) #user to be edited
    online_user = get_jwt_identity() 
    current_user = User.get_or_none(User.id == online_user['id']) #user that is editing
    
    if user: #check existence of user
        if (user.id == current_user.id) or (user.guardian == current_user): #check editing user is user himself or his guardian (if not, 401)
            #set attributes that is 'sure have'
            user.name = request.json.get('name')
            user.password = request.json.get('password')
            user.email = request.json.get('email')
            user.gender = request.json.get('gender')
            if user.save(): # save the fields in user table first
                response = {
                    "message": "Successfully edited user.",
                    "status": "success"
                }
            else:
                response = user.error()
        else:
            response = {
                "message": "401 Unauthorized",
                "status": "fail"
            }
    else:
        response = {
            "message": "User not found, please try again",
            "status": "fail"
        }
    return jsonify(response)

@users_api_blueprint.route('/show', methods=['GET']) #previously is show_patient, now open to all roles
@jwt_required
def show():
    user_ic = request.args.get("ic_number")
    user = User.get_or_none(User.ic_number == user_ic) #user to be shown
    if user:
        response = {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "ic_number": user.ic_number,
            "gender": user.gender,
            "role": user.role,
            "disease": user.disease,
        }
        if user.guardian: #append guardian if there is one, else append as none
            response['guardian'] = user.guardian.name                        
        else:
            response['guardian'] = None
    else:
        response = {
            "message": "User not found",
            "status": "fail"
        }
    return jsonify(response)


@users_api_blueprint.route('/show_my_patient', methods=['GET'])
@jwt_required
def show_my_patient():
    online_user = get_jwt_identity()
    guardian = User.get_or_none(User.id == online_user['id'])

    if guardian:
        patient_list = guardian.my_patient
        if patient_list:
            my_patient = []
            for i in range(len(patient_list)):
                p = User.get_or_none(User.id == patient_list[i])
                my_patient.append(
                    {
                        "id": p.id,
                        "name": p.name,
                        "email": p.email,
                        "ic_number": p.ic_number,
                        "gender": p.gender,
                        "disease": p.disease,
                    }
                )
            response = {
                "status": "success",
                "my_patient": my_patient
            }
        else:
            response = {
                "message": "This guardian has no patient",
                "status": "fail"
            }
    else:
        response = {
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
            "role": user.role,
            "disease": user.disease,
            "gender": user.gender
        }
        if user.guardian: #append guardian if there is one, else append as none
            response['guardian'] = user.guardian.name                        
        else:
            response['guardian'] = None
    else:
        response = {
            "message": "User not found",
            "status": "fail"
        }
    return jsonify(response)

###### Checking for input validation starts below ######

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
    # guardian req: role = patient or guardian
    user = User.get_or_none(User.ic_number == input)
    if user:
        role_list = UserRole.select().where(UserRole.user_id == user.id)  # select all existing role(s)
        role_id_list = []
        for r in role_list:
            role_id_list.append(r.role_id)
        if 1 in role_id_list or 2 in role_id_list:
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