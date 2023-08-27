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
    premium = fields.BooleanField(default=False)
    waktu_basi_premium = fields.DatetimeField(null=True)
    token_konfirmasi = fields.CharField(max_length=225, null=True)
    status = fields.BooleanField(default=False)
    ban = fields.BooleanField(default=False)

    class Meta:
        table = "userdata"

    def __str__(self):
        return self.user_id

class access_token_data(Model):
    access_token = fields.UUIDField(pk=True)
    waktu_basi = fields.DatetimeField()
    user_id = fields.CharField(max_length=225)
    
    class Meta:
        table = "access_token"
        
    def __str__(self):
        return self.access_token