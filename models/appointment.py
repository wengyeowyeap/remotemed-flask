from models.base_model import BaseModel
import peewee as pw
from models.user import User
from models.user_role import UserRole
from models.role import Role
from datetime import datetime
from playhouse.hybrid import hybrid_property

class Appointment(BaseModel):
  doctor = pw.ForeignKeyField(User, null=False)
  patient = pw.ForeignKeyField(User, null=False)
  start_datetime = pw.DateTimeField(null=False)
  end_datetime = pw.DateTimeField(null=False)

  def validate(self):
    #check if 'doctor' entered is a doctor
    is_doctor = UserRole.get_or_none((UserRole.user_id == self.doctor) & (UserRole.role_id == 3))
    if not is_doctor:
      self.errors.append("IC entered does not belong to a doctor.")

    #check if 'patient' entered is a patient
    is_patient = UserRole.select().where((UserRole.user_id == self.patient) & (UserRole.role_id == 1))
    if not is_patient:
      self.errors.append("IC entered does not belong to a patient.")
    
    start = datetime.strptime(self.start_datetime, '%Y-%m-%d %H:%M:%S')
    end = datetime.strptime(self.end_datetime, '%Y-%m-%d %H:%M:%S')

    #basic validation for start and end
    if start == end:
      self.errors.append("The start time and end time is the same.")  
    if start > end:
      self.errors.append("The start time is later than end time.")
    if start.day != end.day:
      self.errors.append("Appointments must be completed within the same day.")

      # CREATE Appointment Validation Pseudocode
      #1. search for all records containing self.doctor, self.patient (if no record, then create appointment)
      #2. convert incoming datetime string into datetime object (to compare with database's DT object)
      #3. Validation:
      #   a. starttime cannot be the same
      #   b. endtime cannot be the same
      #   c. self.start cannot in between record's start and record's end
      #   d. self.end cannot in between record's start and record's end
      #   e. record's start cannot in between self.start and self.end
      #   f. record's end cannot in between self.start and self.end

      #EDIT Appointment Validation Pseudocode
      # Same as CREATE, but exclude the appointment to be edited from query

    if self.id: #if there is self.id --> *EDIT* appointment validation      
      existing_appointments = Appointment.select().where(((Appointment.doctor == self.doctor) | (Appointment.patient == self.patient)) & (~(Appointment.id == self.id))) 
      if existing_appointments > 0:
        for a in existing_appointments: #loop through the records containing self.doctor, self.patient
          if (start == a.start_datetime) or (end == a.end_datetime) or (start > a.start_datetime and start < a.end_datetime) or (end > a.start_datetime and end < a.end_datetime) or (a.start_datetime > start and a.start_datetime < end) or (a.end_datetime > start and a.end_datetime < end): 
            self.errors.append("Appointment time slot not available.")
      else:
        print('No other appointments for these doctor and patient. Validation passed.')
    else: #if there is no self.id --> *CREATE* appointment validation
      existing_appointments = Appointment.select().where((Appointment.doctor == self.doctor) | (Appointment.patient == self.patient))  
      if existing_appointments > 0:
        for a in existing_appointments: #loop through the records containing self.doctor, self.patient
          if (start == a.start_datetime) or (end == a.end_datetime) or (start > a.start_datetime and start < a.end_datetime) or (end > a.start_datetime and end < a.end_datetime) or (a.start_datetime > start and a.start_datetime < end) or (a.end_datetime > start and a.end_datetime < end): 
            self.errors.append("Appointment time slot not available.")
      else:
        print('No appointments for these doctor and patient. Validation passed.')

    print(self.errors)

  @hybrid_property
  def record(self):
    from models.record import Record
    from models.patient_photo import Patient_Photo
    r = Record.get_or_none(Record.appointment_id == self.id)
    photo_list = []
    photo = Patient_Photo.select().where(Patient_Photo.record == r)
    for p in photo:
        photo_list.append(p.full_image_url)
    result = {
      "record_id": r.id,
      "appointment_id": r.appointment_id,
      "report": r.report,
      "prescription": r.prescription,
      "payment_amount": str(r.payment_amount),
      "paid": r.paid,
      "cholestrol_level": str(float(r.cholestrol_level)),
      "sugar_level": str(float(r.sugar_level)),
      "systolic_blood_pressure": str(float(r.systolic_blood_pressure)),
      "diastolic_blood_pressure": str(float(r.diastolic_blood_pressure)),
      "doctor_name": r.appointment.doctor.name,
      "doctor_ic": r.appointment.doctor.ic_number,
      "patient_name": r.appointment.patient.name,
      "patient_ic": r.appointment.patient.ic_number,
      "record_photo": photo_list
    }

    return result

  def error(self):
    error_message = []
    for error in self.errors:
        error_message.append(error)
    response = {
        "message": error_message,
        "status": "fail"
    }
    return response