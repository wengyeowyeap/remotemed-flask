from models.base_model import BaseModel
import peewee as pw

class User(BaseModel):
    name = pw.CharField(unique=True, null=False)
    email = pw.CharField(unique=True, null=False)
    password_hash = pw.TextField(null=False)
    password = None
    ic_number = pw.TextField(unique=True, null=False)
    gender = pw.CharField(null=False)
    guardian = pw.ForeignKeyField('self', null=True, backref='guardian')