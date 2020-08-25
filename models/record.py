from models.base_model import BaseModel
import peewee as pw
from models.appointment import Appointment

class Record(BaseModel):
  appointment = pw.ForeignKeyField(Appointment, unique=True, backref="appointment")
  report = pw.TextField(null=True)
  prescription = pw.TextField(null=True)
  payment_amount = pw.DecimalField(default=0)
  paid = pw.BooleanField(default=False)
  cholestrol_level = pw.DecimalField()
  sugar_level = pw.DecimalField()
  systolic_blood_pressure = pw.IntegerField()
  diastolic_blood_pressure = pw.IntegerField()
