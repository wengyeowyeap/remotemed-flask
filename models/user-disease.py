from models.base_model import BaseModel
import peewee as pw
from models.user import User
from models.disease import Disease

class UserDisease(BaseModel):
  user = pw.ForeignKeyField(User, backref="user", on_delete="CASCADE")
  disease = pw.ForeignKeyField(Disease, backref="disease", on_delete="CASCADE")