from models.base_model import BaseModel
import peewee as pw
from models.user import User
from models.role import Role

class User-Role(BaseModel):
  user = pw.ForeignKeyField(User, backref="user", on_delete="CASCADE")
  role = pw.ForeignKeyField(Role, backref="role", on_delete="CASCADE")