from models.base_model import BaseModel
import peewee as pw
from models.appointment import Appointment
from playhouse.hybrid import hybrid_property

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

  def validate(self):
    #validate payment amount
    if (self.payment_amount) or (self.payment_amount == 0): #check if amount is inputted, and also allow 0 to be saved (0 is falsy)
      if self.payment_amount == 0: #if there is no payment_amount, change paid state to True
        self.paid = True
      self.payment_amount =  round(self.payment_amount, 2) #round to 2 decimal places before saving
    else:
      self.errors.append('No payment is inputted.')

  @hybrid_property
  def photo(self):
    from models.patient_photo import Patient_Photo
    photo_list = []
    photo = Patient_Photo.select().where(Patient_Photo.record == self)
    for p in photo:
        photo_list.append(p.full_image_url)
    return photo_list