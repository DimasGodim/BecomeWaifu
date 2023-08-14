from tortoise.models import Model
from tortoise import fields

class logaudio(Model):
    audio_id = fields.IntField()
    user_id = fields.CharField(max_length=225)
    transcript = fields.CharField(max_length=225)
    translate = fields.CharField(max_length=225)
    audio_file = fields.BinaryField()

    class Meta:
        table = "logaudio"
    
    def __str__(self):
        return self.audio_id

class userdata(Model):
    user_id = fields.UUIDField(pk=True)
    nama = fields.CharField(max_length=225, null=True)
    email = fields.CharField(max_length=225)
    password = fields.BinaryField(max_length=225,null=True)
    akunbw = fields.BooleanField(default=False)
    token = fields.CharField(max_length=225, null=True)
    waktu_basi = fields.DatetimeField(null=True)
    status = fields.BooleanField(default=False)
    ban = fields.BooleanField(default=False)

    class Meta:
        table = "userdata"

    def __str__(self):
        return self.user_id
