from models.base_model import BaseModel
import peewee as pw
from models.record import Record

class Patient_Photo(BaseModel):
  record = pw.ForeignKeyField(Record, backref="record")
  image_url = pw.TextField(null=True)
  caption = pw.CharField(null=True)