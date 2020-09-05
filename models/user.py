from models.base_model import BaseModel
import peewee as pw
import re
from werkzeug.security import generate_password_hash
from datetime import datetime

class User(BaseModel):
    name = pw.CharField(null=False)
    email = pw.CharField(unique=True, null=False)
    password_hash = pw.TextField(null=False)
    password = None
    ic_number = pw.TextField(unique=True, null=False)
    gender = pw.CharField(null=False)
    guardian = pw.ForeignKeyField('self', null=True)

    def validate(self):
        #validate ic_number
        ic_number_duplicate = User.get_or_none(User.ic_number == self.ic_number)
        if self.ic_number: #check if IC is inputted
            if re.search(r"([0-9]){2}([0-1]){1}([0-9]){1}([0-3]){1}([0-9]){7}", self.ic_number): #check IC format
                if ic_number_duplicate and ic_number_duplicate.id != self.id: #check duplicate, skip condition if IC user is same as entering user
                    self.errors.append('Ic_number has been used.')
                else:
                    pass
            else:
                self.errors.append('Ic_number has wrong format.')
        else:
            self.errors.append('No ic_number is inputted.')

        #validate email
        email_duplicate = User.get_or_none(User.email == self.email)
        if self.email: #check if email is inputted
            if re.search(r"^\w+([.-]?\w+)*@\w+([.-]?\w+)*(\.\w{2,3})+$", self.email): #check email format
                if email_duplicate and email_duplicate.id != self.id: #check duplicate, skip condition if email user is same as entering user
                    self.errors.append('Email has been used.')
                else:
                    pass
            else:
                self.errors.append('Email has wrong format.')
        else:
            self.errors.append('No email is inputted.')            

        #validate password
        if self.password: #check if password is inputted
            if (len(self.password) < 6) or (re.search('[A-Z]', self.password) is None) or (re.search('[a-z]', self.password) is None) or (re.search('[0-9]', self.password) is None) or (re.search('[!@#$%]', self.password) is None): #check pw format
                self.errors.append('Password requirement: 6 or more characters, uppercase letters, lowercase letters, numbers, special characters(!@#$%)')
            else:
                self.password_hash = generate_password_hash(self.password)  #hash the password to be stored in database
        
        #validate gender
        if self.gender != 'male': #check if gender is a male string
            if self.gender != 'female': #check if gender is a female string
                self.errors.append("Input is not 'male' or 'female'")
    
    def role(self):
        from models.user_role import UserRole
        from models.role import Role
        role_list = Role.select().join(UserRole).where(UserRole.user == self)
        role_name_list = []
        for r in role_list:
            role_name_list.append(r.role_name)
        return role_name_list #["patient", "guardian"]

    def disease(self):
        from models.user_disease import UserDisease
        from models.disease import Disease
        disease_list = Disease.select().join(UserDisease).where(UserDisease.user == self)
        disease_name_list = []
        for d in disease_list:
            disease_name_list.append(d.disease_name)
        return disease_name_list #["diabetes", "hypertension"]

    def upcoming_appointment(self):
        from models.appointment import Appointment
        upcoming_appointment = Appointment.select().where((Appointment.doctor == self) | (Appointment.patient == self))
        upcoming_appointment_list = []
        for a in upcoming_appointment:
            if a.end_datetime > datetime.now():
                upcoming_appointment_list.append({
                                "appointment_id": a.id,
                                "doctor_name": a.doctor.name,
                                "doctor_ic": a.doctor.ic_number,
                                "patient_name": a.patient.name,
                                "patient_ic": a.patient.ic_number,
                                "start_time": a.start_datetime.strftime("%Y-%m-%d %H:%M:%S"),
                                "end_time": a.end_datetime.strftime("%Y-%m-%d %H:%M:%S")
                            })
        return upcoming_appointment_list
    
    def past_appointment(self):
        from models.appointment import Appointment
        past_appointment = Appointment.select().where((Appointment.doctor == self) | (Appointment.patient == self))
        past_appointment_list = []
        for a in past_appointment:
            if a.end_datetime < datetime.now():
                past_appointment_list.append({
                                "appointment_id": a.id,
                                "doctor_name": a.doctor.name,
                                "doctor_ic": a.doctor.ic_number,
                                "patient_name": a.patient.name,
                                "patient_ic": a.patient.ic_number,
                                "start_time": a.start_datetime.strftime("%Y-%m-%d %H:%M:%S"),
                                "end_time": a.end_datetime.strftime("%Y-%m-%d %H:%M:%S")
                            })
        return past_appointment_list
    
    def record(self):
        from models.record import Record
        from models.appointment import Appointment
        from models.patient_photo import Patient_Photo
        record = Record.select().join(Appointment).where((Appointment.doctor == self) | (Appointment.patient == self))
        record_list = []
        for r in record:
            photo_list = []
            photo = Patient_Photo.select().where(Patient_Photo.record == r)
            for p in photo:
                photo_list.append(p.full_image_url)
            record_list.append({
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
                        })
        return record_list
    
    def my_patient(self):
        patient = User.select().where(User.guardian == self)
        patient_list = []
        for p in patient:
            patient_list.append(p.id)
        return patient_list #Using the id, can get other things through above methods