import os
from flask import Blueprint, request, jsonify
from models.user import User
from models.record import Record
import braintree
from remotemed_api.util.braintree_helpers import generate_client_token, transact
from remotemed_api.util.mailgun_helper import send_donation_message
from flask_jwt_extended import jwt_required, get_jwt_identity

payments_api_blueprint = Blueprint('payments_api',
                             __name__,
                             template_folder='templates')

TRANSACTION_SUCCESS_STATUSES = [
    braintree.Transaction.Status.Authorized,
    braintree.Transaction.Status.Authorizing,
    braintree.Transaction.Status.Settled,
    braintree.Transaction.Status.SettlementConfirmed,
    braintree.Transaction.Status.SettlementPending,
    braintree.Transaction.Status.Settling,
    braintree.Transaction.Status.SubmittedForSettlement
]

@payments_api_blueprint.route('/new', methods=['GET'])
@jwt_required
def new():
  online_user = get_jwt_identity()
  user = User.get_or_none(User.id == online_user['id'])

  if user:
    if user.id == online_user['id']:
      client_token = generate_client_token()
    elif: user.guardian_id == online_user['id']:
      client_token = generate_client_token()
    else:
      response = {
        "message" = "User is unauthorized",
        "status" = "fail"
      }
  else:
    response={
      "message": "user not exist"
      "status": "fail"
    }

@payments_api_blueprint.route('/', methods=['POST'])
@jwt_required
def create():
  amount = request.json("amount")
  nonce_from_the_client = request.json("payment_method_nonce")
  result = transact({
    "amount": amount,
    "payment_method_nonce": nonce_from_the_client,
    "options": {
      "submit_for_settlement": True
    }
  })

  if result.is_success or result.transaction:
    record = Record.get_or_none(Record.id == request.json("record_id"))
    record.paid = True
    if record.save():
      response = {
        message="payment successful",
        status="success"
      }
  else:
    for x in result.errors.deep_errors: flash('Error: %s: %s' % (x.code, x.message))
