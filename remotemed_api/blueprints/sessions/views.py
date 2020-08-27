from flask import Blueprint, request, jsonify
from models.user import User
from models.user_role import UserRole
from models.role import Role
from models.disease import Disease
from models.user_disease import UserDisease
from werkzeug.security import check_password_hash
from flask_jwt_extended import create_access_token

sessions_api_blueprint = Blueprint('sessions_api',
                             __name__,
                             template_folder='templates')

@sessions_api_blueprint.route('/login', methods=['POST'])
def login():
    params = request.json
    ic_number = params.get("ic_number")
    password = params.get("password")

    user = User.get_or_none(User.ic_number==ic_number)
    if user:
        result = check_password_hash(user.password_hash, password)
        if result:
            user_role_list =[]
            user_role = Role.select().join(UserRole).where(UserRole.user_id==user.id)
            for role in user_role:
                user_role_list.append(role.id)
            if (1 in user_role_list) and (2 in user_role_list):
                role_name_list = []
                role_list = Role.select().join(UserRole).where(UserRole.user_id == user.id)
                for role in role_list:
                    role_name_list.append(role.role_name)
                diseases_name_list = []
                diseases_list = Disease.select().join(UserDisease).where(UserDisease.user_id == user.id)
                for disease in diseases_list:
                    diseases_name_list.append(disease.disease_name)
                if user.guardian_id != None:
                    guardian = user.guardian_id
                else:
                    guardian = None

                identity = {
                    "id": user.id,
                    "name": user.name,
                    "email": user.email,
                    "ic_number": user.ic_number,
                    "gender": user.gender,
                    "role": role_name_list,
                    "disease": diseases_name_list,
                    "guardian": guardian
                }

                token = create_access_token(identity=identity)
                return jsonify({
                    "auth_token": token,
                    "message": "Successfully signed in.",
                    "status": "success",
                    "user": {
                        "id": user.id,
                        "name": user.name,
                        "email": user.email,
                        "ic_number": user.ic_number,
                        "gender": user.gender,
                        "role": role_name_list,
                        "disease": diseases_name_list,
                        "guardian": guardian
                    }
                })

            if 1 in user_role_list:
                role_name_list = []
                role_list = Role.select().join(UserRole).where(UserRole.user_id == user.id)
                for role in role_list:
                    role_name_list.append(role.role_name)
                diseases_name_list = []
                diseases_list = Disease.select().join(UserDisease).where(UserDisease.user_id == user.id)
                for disease in diseases_list:
                    diseases_name_list.append(disease.disease_name)

                identity = {
                    "id": user.id,
                    "name": user.name,
                    "email": user.email,
                    "ic_number": user.ic_number,
                    "gender": user.gender,
                    "role": role_name_list,
                    "disease": diseases_name_list
                }

                token = create_access_token(identity=identity)
                return jsonify({
                    "auth_token": token,
                    "message": "Successfully signed in.",
                    "status": "success",
                    "user": {
                        "id": user.id,
                        "name": user.name,
                        "email": user.email,
                        "ic_number": user.ic_number,
                        "gender": user.gender,
                        "role": role_name_list,
                        "disease": diseases_name_list
                    }
                })

            if (2 in user_role_list) or (3 in user_role_list) or (4 in user_role_list):
                role_name_list = []
                role_list = Role.select().join(UserRole).where(UserRole.user_id == user.id)
                for role in role_list:
                    role_name_list.append(role.role_name)

                identity = {
                    "id": user.id,
                    "name": user.name,
                    "email": user.email,
                    "ic_number": user.ic_number,
                    "gender": user.gender,
                    "role": role_name_list,
                }

                token = create_access_token(identity=identity)
                return jsonify({
                    "auth_token": token,
                    "message": "Successfully signed in.",
                    "status": "success",
                    "user": {
                        "id": user.id,
                        "name": user.name,
                        "email": user.email,
                        "ic_number": user.ic_number,
                        "gender": user.gender,
                        "role": role_name_list,
                    }
                })
            


        else:
            return jsonify({
                        "message": "Wrong Password, Please try again.",
                        "status": "failed"
                    })
    else:
        return jsonify({
                        "message": "No such user exists.",
                        "status": "failed"
                    })
            
    