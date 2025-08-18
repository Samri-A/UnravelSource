from django.db import models

class files(models.Model):
    id = models.AutoField(primary_key=True )
    repo = models.CharField(max_length=255)
    branch = models.CharField(max_length=255)
    path = models.CharField(max_length=255)
    content = models.TextField()
