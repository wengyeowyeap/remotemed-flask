from models.base_model import BaseModel
import peewee as pw
from models.record import Record
from playhouse.hybrid import hybrid_property

class Patient_Photo(BaseModel):
  record = pw.ForeignKeyField(Record, backref="record")
  image_url = pw.TextField(null=True)
  caption = pw.CharField(null=True)

  @hybrid_property
  def full_image_url(self):
      if self.image_url:
          from app import app
          return app.config.get("S3_LOCATION") + self.image_url
      else:
          return ""