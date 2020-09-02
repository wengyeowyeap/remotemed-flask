from models.base_model import BaseModel
import peewee as pw
from models.appointment import Appointment

class Record(BaseModel):
  appointment = pw.ForeignKeyField(Appointment, unique=True, backref="appointment")
  report = pw.TextField(null=True)
  prescription = pw.TextField(null=True)
  payment_amount = pw.DecimalField(default=0)
  paid = pw.BooleanField(default=False)
  cholestrol_level = pw.DecimalField(null=True)
  sugar_level = pw.DecimalField(null=True)
  systolic_blood_pressure = pw.IntegerField(null=True)
  diastolic_blood_pressure = pw.IntegerField(null=True)
  zoom_url = pw.TextField(null=True)
