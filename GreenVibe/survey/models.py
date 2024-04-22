from django.db import models

class Heading(models.Model):
    heading = models.CharField(max_length=100)

    def __str__(self):
        return self.heading
    
class Question(models.Model):
    question = models.CharField(max_length=200)
    heading = models.ForeignKey(Heading, on_delete=models.CASCADE, default=1)
    answer1 = models.CharField(max_length=100)
    answer2 = models.CharField(max_length=100)
    answer3 = models.CharField(max_length=100, null=True, blank=True)
    answer4 = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return self.question
 