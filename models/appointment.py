from models.base_model import BaseModel
import peewee as pw
from models.user import User
from models.user_role import UserRole
from models.role import Role
import datetime

class Appointment(BaseModel):
  doctor = pw.ForeignKeyField(User, backref='doctor', null=False)
  patient = pw.ForeignKeyField(User, backref='patient', null=False)
  start_datetime = pw.DateTimeField(null=False)
  end_datetime = pw.DateTimeField(null=False)

  def validate(self):
    is_doctor = UserRole.get_or_none(UserRole.user_id==self.doctor, UserRole.role_id==3)
    if not is_doctor:
      self.errors.append("This is not a doctor's id")

    is_patient = UserRole.select().where(UserRole.user_id==self.patient, UserRole.role_id==1)
    if not is_patient:
      self.errors.append("This is not a patient's id")
    
    current_datetime = datetime.datetime.now()
    
    existing_doctor_appointments = Appointment.select().where(Appointment.doctor_id==self.doctor)
    for a in existing_doctor_appointments:
      starttime = datetime.datetime.strptime(self.start_datetime, '%Y-%m-%d %H:%M:%S')
      endtime = datetime.datetime.strptime(self.end_datetime, '%Y-%m-%d %H:%M:%S')
      if starttime > a.start_datetime and starttime < a.end_datetime:
        self.errors.append("This doctor already has an appointment that crashed the time you've entered.")
      elif endtime > a.start_datetime and endtime < a.end_datetime:
        self.errors.append("This doctor already has an appointment that crashed the time you've entered.")
      elif a.start_datetime > starttime and a.end_datetime < endtime:
        self.errors.append("This doctor already has an appointment that crashed the time you've entered.")
    
    existing_patient_appointments = Appointment.select().where(Appointment.patient_id==self.patient)
    for a in existing_patient_appointments:
      starttime = datetime.datetime.strptime(self.start_datetime, '%Y-%m-%d %H:%M:%S')
      endtime = datetime.datetime.strptime(self.end_datetime, '%Y-%m-%d %H:%M:%S')
      if starttime > a.start_datetime and starttime < a.end_datetime:
        self.errors.append("This patient already has an appointment that crashed the time you've entered.")
      elif endtime > a.start_datetime and endtime < a.end_datetime:
        self.errors.append("This patient already has an appointment that crashed the time you've entered.")
      elif a.start_datetime > starttime and a.end_datetime < endtime:
        self.errors.append("This patient already has an appointment that crashed the time you've entered.")

    
    duplicate_time = Appointment.get_or_none(Appointment.start_datetime==self.start_datetime, Appointment.end_datetime==self.end_datetime, Appointment.patient_id==self.patient, Appointment.doctor_id==self.doctor)
    if duplicate_time:
      self.errors.append("duplicate record!")

    duplicate_doctor_time = Appointment.get_or_none(Appointment.start_datetime==self.start_datetime, Appointment.doctor_id==self.doctor) or Appointment.get_or_none(Appointment.end_datetime==self.end_datetime, Appointment.doctor_id==self.doctor)
    if duplicate_doctor_time:
      self.errors.append("This doctor already has an appointment which have the exactly same starting time or ending time.")
    
    duplicate_patient_time = Appointment.get_or_none(Appointment.start_datetime==self.start_datetime, Appointment.end_datetime==self.end_datetime, Appointment.patient_id==self.patient)
    if duplicate_patient_time:
      self.errors.append("This patient already has an appointment which have the exactly same starting time and ending time.")

    same_start_end_time = (self.start_datetime == self.end_datetime)
    if same_start_end_time:
      self.errors.append("Starting time and ending time cannot be the same.")

    start_time = self.start_datetime
    end_time = self.end_datetime
    if not (start_time[0:10]) == (end_time[0:10]):
      self.errors.append("Appointment must be finished within a day.")
  




    