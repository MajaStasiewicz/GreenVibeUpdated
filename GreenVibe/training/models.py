from django.db import models

class Video(models.Model):
    caption=models.CharField(max_length=100)
    videoMan=models.FileField(upload_to="video/%y")
    videoWoman=models.FileField(upload_to="video/%y")
    width=models.PositiveIntegerField()  
    height=models.PositiveIntegerField()
    title=models.CharField(max_length=100, default="ćwiczenia")
    description=models.TextField(default="opis")

    def __str__(self):
        return self.caption
    
