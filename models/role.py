from models.base_model import BaseModel
import peewee as pw

class Role(BaseModel):
  role_name = pw.CharField(null=False)