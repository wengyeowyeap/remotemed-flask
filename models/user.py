from models.base_model import BaseModel
import peewee as pw
import re
from werkzeug.security import generate_password_hash

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
