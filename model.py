from tortoise.models import Model
from tortoise import fields

class logaudio(Model):
    id = fields.UUIDField(pk=True)
    transcript = fields.CharField(max_length=225)
    translate = fields.CharField(max_length=225)
    audio_file = fields.BinaryField()

    class Meta:
        table = "logaudio"
    
    def __str__(self):
        return self.id

class userdata(Model):
    id = fields.UUIDField(pk=True)
    nama = fields.CharField(max_length=225)
    email = fields.CharField(max_length=225)

    class Meta:
        table = "userdata"

    def __str__(self):
        return self.id
