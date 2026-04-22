from django.db import models

# Create your models here.

class Category(models.Model):
    name = models.CharField(max_length=255)
    parent_id = models.ForeignKey('self', on_delete=models.CASCADE)

    def __str__(self):
        return self.name