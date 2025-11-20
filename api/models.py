from django.db import models


# id sa automatický pridelí
class Test(models.Model):
    meno = models.CharField(max_length=50)
    body = models.IntegerField()

    def __strin__(self):
        return self.meno
