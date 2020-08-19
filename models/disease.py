from models.base_model import BaseModel
import peewee as pw

class Disease(BaseModel):
  disease_name = pw.CharField(unique=True, null=False)