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

    user = User.get_or_none(User.ic_number == ic_number)
    if user:
        result = check_password_hash(user.password_hash, password)
        if result:
                if user.guardian_id != None:
                    guardian = user.guardian.name
                else:
                    guardian = None

                identity = {
                    "id": user.id,
                    "name": user.name,
                    "email": user.email,
                    "ic_number": user.ic_number,
                    "gender": user.gender,
                    "role": user.role, #hybrid property
                    "disease": user.disease, #hybrid property
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
                        "role": user.role, #hybrid property
                        "disease": user.disease, #hybrid property
                        "guardian": guardian
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
