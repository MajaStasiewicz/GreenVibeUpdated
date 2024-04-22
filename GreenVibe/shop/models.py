from django.db import models

class ZapisNewsletter(models.Model):
    email = models.CharField(max_length=200)

    def __str__(self):
        return self.email

class Banner(models.Model):
    image = models.ImageField(upload_to='images/banners/')
    is_active = models.BooleanField(default=True)