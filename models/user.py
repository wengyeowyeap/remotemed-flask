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
    guardian = pw.ForeignKeyField('self', null=True, backref='guardian')

    def validate(self):
        ic_number_duplicate = User.get_or_none(User.ic_number == self.ic_number)
        email_duplicate = User.get_or_none(User.email == self.email)

        if ic_number_duplicate and email_duplicate:
            self.errors.append('Ic_number and email has been used')
        elif ic_number_duplicate:
            self.errors.append('Ic_number has been used')
        elif email_duplicate:
            self.errors.append('Email has been used')
        
        if self.password:
            if (len(self.password) < 6) or (re.search('[A-Z]',self.password) is None) or (re.search('[a-z]',self.password) is None) or (re.search('[0-9]',self.password) is None) or (re.search('[!@#$%]',self.password) is None):
                self.errors.append('Password requirement: 6 or more characters, uppercase letters, lowercase letters, numbers, special characters(!@#$%)')
            else:
                self.password_hash = generate_password_hash(self.password) # store this in database  

        if self.gender != 'male':
            if self.gender != 'female':
                self.errors.append("Please input 'male' or 'female'")
