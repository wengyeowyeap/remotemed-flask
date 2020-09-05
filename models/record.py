from models.base_model import BaseModel
import peewee as pw
from models.appointment import Appointment

class Record(BaseModel):
  appointment = pw.ForeignKeyField(Appointment, unique=True, backref="appointment")
  report = pw.TextField(null=True)
  prescription = pw.TextField(null=True)
  payment_amount = pw.DecimalField(default=0, decimal_places=2)
  paid = pw.BooleanField(default=False)
  cholestrol_level = pw.DecimalField(null=True)
  sugar_level = pw.DecimalField(null=True)
  systolic_blood_pressure = pw.IntegerField(null=True)
  diastolic_blood_pressure = pw.IntegerField(null=True)
  zoom_url = pw.TextField(null=True)

  def validate(self):
    #validate payment amount
    if (self.payment_amount) or (self.payment_amount == 0): #check if amount is inputted, and also allow 0 to be saved (0 is falsy)
      if self.payment_amount == 0: #if there is no payment_amount, change paid state to True
        self.paid = True
      self.payment_amount =  round(self.payment_amount, 2) #round to 2 decimal places before saving
    else:
      self.errors.append('No payment is inputted.')