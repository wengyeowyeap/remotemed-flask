from models.base_model import BaseModel
import peewee as pw
from models.user import User
from models.disease import Disease

class UserDisease(BaseModel):
  user = pw.ForeignKeyField(User, on_delete="CASCADE")
  disease = pw.ForeignKeyField(Disease, on_delete="CASCADE")