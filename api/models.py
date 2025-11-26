from django.db import models


class Test(models.Model):
    meno = models.CharField(max_length=50)
    body = models.IntegerField()

    def __str__(self):
        return self.meno
