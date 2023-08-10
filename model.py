from tortoise.models import Model
from tortoise import fields

class logaudio(Model):
    audio_id = fields.IntField(pk=True)
    user_id = fields.CharField(max_length=225)
    transcript = fields.CharField(max_length=225)
    translate = fields.CharField(max_length=225)
    audio_file = fields.BinaryField()

    class Meta:
        table = "logaudio"
    
    def __str__(self):
        return self.id

class userdata(Model):
    user_id = fields.UUIDField(pk=True)
    nama = fields.CharField(max_length=225, null=True)
    email = fields.CharField(max_length=225)
    password = fields.CharField(max_length=255, null=True)
    akun_bw = fields.BooleanField(default=False)

    class Meta:
        table = "userdata"

    def __str__(self):
        return self.id