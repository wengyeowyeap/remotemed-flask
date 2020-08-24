from models.base_model import BaseModel
import peewee as pw
from models.user import User
from models.user_role import UserRole
import datetime

class Appointment(BaseModel):
  doctor = pw.ForeignKeyField(User, backref='doctor', null=False)
  patient = pw.ForeignKeyField(User, backref='patient', null=False)
  start_datetime = pw.DateTimeField(null=False)
  end_datetime = pw.DateTimeField(null=False)


